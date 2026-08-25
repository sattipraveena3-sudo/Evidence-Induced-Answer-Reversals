from ear.gate import (
    EvidenceStabilityGate,
    FixedDecisionVerifier,
    GateState,
    LexicalChangeVerifier,
    ModelChangeVerifier,
    Verification,
    answer_support,
)


def test_answer_support_and_lexical_decisions():
    evidence = ["The Trial was written by Franz Kafka."]
    assert answer_support("Franz Kafka", evidence) == 1.0
    assert answer_support("Albert Camus", evidence) == 0.0

    verifier = LexicalChangeVerifier(support_threshold=0.8, margin=0.2)
    retained = verifier.verify(
        "Who wrote The Trial?", evidence, "Franz Kafka", "Albert Camus"
    )
    assert retained.decision == "retain_previous"

    accepted = verifier.verify(
        "Who wrote The Trial?", evidence, "unknown", "Franz Kafka"
    )
    assert accepted.decision == "accept_new"

    conflicting = verifier.verify(
        "Who wrote The Trial?",
        ["One source says Franz Kafka; another says Albert Camus."],
        "Franz Kafka",
        "Albert Camus",
    )
    assert conflicting.decision == "abstain"


def test_gate_triggers_only_on_normalized_answer_change():
    class CountingVerifier:
        def __init__(self):
            self.calls = 0

        def verify(self, question, passages, previous_answer, new_answer):
            self.calls += 1
            return Verification(
                "retain_previous", 1.0, 0.0, "Previous answer is supported."
            )

    verifier = CountingVerifier()
    gate = EvidenceStabilityGate(verifier)
    state = GateState()

    initial = gate.apply(state, "Question", ["Evidence"], "Franz Kafka")
    unchanged = gate.apply(state, "Question", ["Evidence"], "franz kafka")
    changed = gate.apply(state, "Question", ["Evidence"], "Albert Camus")

    assert initial.decision == "initial" and not initial.triggered
    assert unchanged.decision == "unchanged" and not unchanged.triggered
    assert changed.decision == "retain_previous" and changed.answer == "franz kafka"
    assert verifier.calls == 1
    assert state.anchor_answer == "franz kafka"


def test_model_verifier_parses_strict_json_response():
    def complete(prompt: str, max_tokens: int) -> str:
        assert "Question: Who wrote The Trial?" in prompt
        assert max_tokens == 180
        return (
            "```json\n"
            '{"decision":"retain_previous","previous_support":0.95,'
            '"new_support":0.1,"reason":"Only the previous answer is supported."}'
            "\n```"
        )

    result = ModelChangeVerifier(complete).verify(
        "Who wrote The Trial?",
        ["The Trial was written by Franz Kafka."],
        "Franz Kafka",
        "Albert Camus",
    )
    assert result.decision == "retain_previous"
    assert result.previous_support == 0.95
    assert result.new_support == 0.1


def test_fixed_sanity_verifiers_are_explicit():
    retained = FixedDecisionVerifier("retain_previous").verify(
        "Question", ["Evidence"], "old", "new"
    )
    abstained = FixedDecisionVerifier("abstain").verify(
        "Question", ["Evidence"], "old", "new"
    )
    assert retained.decision == "retain_previous"
    assert abstained.decision == "abstain"

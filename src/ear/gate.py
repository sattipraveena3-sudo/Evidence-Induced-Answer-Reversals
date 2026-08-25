from __future__ import annotations

import json
import re
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from .scoring import normalize_answer

VALID_DECISIONS = {"accept_new", "retain_previous", "abstain"}
UNANSWERED = {
    "",
    "unknown",
    "insufficient evidence",
    "cannot determine",
    "not enough information",
}


@dataclass(frozen=True)
class Verification:
    decision: str
    previous_support: float
    new_support: float
    reason: str

    def __post_init__(self) -> None:
        if self.decision not in VALID_DECISIONS:
            raise ValueError(f"Invalid gate decision: {self.decision}")
        for name, value in (
            ("previous_support", self.previous_support),
            ("new_support", self.new_support),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


class ChangeVerifier(Protocol):
    def verify(
        self,
        question: str,
        passages: list[str],
        previous_answer: str,
        new_answer: str,
    ) -> Verification: ...


@dataclass
class GateState:
    """Per-example state for the last non-abstained answer."""

    anchor_answer: str | None = None


@dataclass(frozen=True)
class GateApplication:
    answer: str
    abstained: bool
    triggered: bool
    decision: str
    anchor_before: str | None
    previous_support: float | None
    new_support: float | None
    reason: str
    latency_ms: float

    def to_dict(self) -> dict[str, object]:
        return {
            "triggered": self.triggered,
            "decision": self.decision,
            "anchor_before": self.anchor_before,
            "previous_support": self.previous_support,
            "new_support": self.new_support,
            "reason": self.reason,
            "latency_ms": self.latency_ms,
        }


def answer_support(answer: str, passages: list[str]) -> float:
    """Return the strongest within-passage lexical support for an answer.

    This deterministic score is a transparent baseline, not an entailment model.
    It never receives a gold answer or correctness label.
    """

    normalized = normalize_answer(answer)
    if normalized in UNANSWERED:
        return 0.0

    answer_tokens = normalized.split()
    answer_counts = Counter(answer_tokens)
    denominator = sum(answer_counts.values())
    if denominator == 0:
        return 0.0

    best = 0.0
    for passage in passages:
        passage_tokens = normalize_answer(passage).split()
        if any(
            passage_tokens[index : index + len(answer_tokens)] == answer_tokens
            for index in range(len(passage_tokens) - len(answer_tokens) + 1)
        ):
            return 1.0
        passage_counts = Counter(passage_tokens)
        overlap = sum((answer_counts & passage_counts).values())
        best = max(best, overlap / denominator)
    return best


class LexicalChangeVerifier:
    """Gold-label-free comparative-support baseline."""

    def __init__(self, support_threshold: float = 0.8, margin: float = 0.2) -> None:
        if not 0.0 <= support_threshold <= 1.0:
            raise ValueError("support_threshold must be between 0 and 1")
        if not 0.0 <= margin <= 1.0:
            raise ValueError("margin must be between 0 and 1")
        self.support_threshold = support_threshold
        self.margin = margin

    def verify(
        self,
        question: str,
        passages: list[str],
        previous_answer: str,
        new_answer: str,
    ) -> Verification:
        del question  # The lexical baseline intentionally scores evidence support only.
        previous_support = answer_support(previous_answer, passages)
        new_support = answer_support(new_answer, passages)

        if (
            new_support >= self.support_threshold
            and new_support - previous_support >= self.margin
        ):
            decision = "accept_new"
            reason = (
                "The new answer has stronger lexical support in the current evidence."
            )
        elif (
            previous_support >= self.support_threshold
            and previous_support - new_support >= self.margin
        ):
            decision = "retain_previous"
            reason = "The previous answer has stronger lexical support in the current evidence."
        else:
            decision = "abstain"
            reason = "Comparative lexical support is insufficient or conflicting."

        return Verification(
            decision=decision,
            previous_support=previous_support,
            new_support=new_support,
            reason=reason,
        )


class FixedDecisionVerifier:
    """Sanity baseline that makes the same decision on every answer change."""

    def __init__(self, decision: str) -> None:
        if decision not in {"retain_previous", "abstain"}:
            raise ValueError("Fixed gate must retain or abstain")
        self.decision = decision

    def verify(
        self,
        question: str,
        passages: list[str],
        previous_answer: str,
        new_answer: str,
    ) -> Verification:
        del question, passages, previous_answer, new_answer
        return Verification(
            decision=self.decision,
            previous_support=0.0,
            new_support=0.0,
            reason=f"Fixed sanity baseline: {self.decision}.",
        )


class ModelChangeVerifier:
    """Evidence verifier backed by a JSON-producing chat completion."""

    def __init__(self, complete: Callable[[str, int], str]) -> None:
        self.complete = complete

    @staticmethod
    def _parse_response(text: str) -> Verification:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Verifier response did not contain a JSON object")
        payload = json.loads(match.group(0))
        return Verification(
            decision=str(payload["decision"]),
            previous_support=float(payload["previous_support"]),
            new_support=float(payload["new_support"]),
            reason=str(payload.get("reason", "")),
        )

    def verify(
        self,
        question: str,
        passages: list[str],
        previous_answer: str,
        new_answer: str,
    ) -> Verification:
        evidence = "\n\n".join(f"[{i + 1}] {p}" for i, p in enumerate(passages))
        prompt = f"""You are an evidence verifier. Compare two candidate answers using only the
provided evidence. Do not use outside knowledge. Choose exactly one decision:
- accept_new: the new answer is better supported;
- retain_previous: the previous answer is better supported;
- abstain: support is insufficient or conflicting.

Return one JSON object and no markdown:
{{"decision":"accept_new|retain_previous|abstain","previous_support":0.0,
"new_support":0.0,"reason":"one short evidence-based sentence"}}

Question: {question}
Previous answer: {previous_answer}
New answer: {new_answer}

Evidence:
{evidence}
"""
        return self._parse_response(self.complete(prompt, 180))


class EvidenceStabilityGate:
    """Apply a verifier only when a candidate differs from the stable anchor."""

    def __init__(
        self, verifier: ChangeVerifier, abstain_answer: str = "unknown"
    ) -> None:
        self.verifier = verifier
        self.abstain_answer = abstain_answer

    def apply(
        self,
        state: GateState,
        question: str,
        passages: list[str],
        candidate_answer: str,
    ) -> GateApplication:
        anchor = state.anchor_answer
        if anchor is None:
            state.anchor_answer = candidate_answer
            return GateApplication(
                answer=candidate_answer,
                abstained=False,
                triggered=False,
                decision="initial",
                anchor_before=None,
                previous_support=None,
                new_support=None,
                reason="Initial answer establishes the comparison anchor.",
                latency_ms=0.0,
            )

        if normalize_answer(candidate_answer) == normalize_answer(anchor):
            state.anchor_answer = candidate_answer
            return GateApplication(
                answer=candidate_answer,
                abstained=False,
                triggered=False,
                decision="unchanged",
                anchor_before=anchor,
                previous_support=None,
                new_support=None,
                reason="The normalized answer did not change.",
                latency_ms=0.0,
            )

        started = time.perf_counter()
        verification = self.verifier.verify(
            question=question,
            passages=passages,
            previous_answer=anchor,
            new_answer=candidate_answer,
        )
        latency_ms = (time.perf_counter() - started) * 1000.0

        if verification.decision == "accept_new":
            state.anchor_answer = candidate_answer
            answer = candidate_answer
            abstained = False
        elif verification.decision == "retain_previous":
            answer = anchor
            abstained = False
        else:
            answer = self.abstain_answer
            abstained = True

        return GateApplication(
            answer=answer,
            abstained=abstained,
            triggered=True,
            decision=verification.decision,
            anchor_before=anchor,
            previous_support=verification.previous_support,
            new_support=verification.new_support,
            reason=verification.reason,
            latency_ms=latency_ms,
        )

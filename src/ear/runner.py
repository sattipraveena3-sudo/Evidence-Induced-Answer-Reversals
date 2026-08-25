from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backends import Backend, make_backend
from .gate import (
    EvidenceStabilityGate,
    FixedDecisionVerifier,
    GateState,
    LexicalChangeVerifier,
    ModelChangeVerifier,
)
from .schema import Example
from .scoring import best_f1, correctness


def parse_depths(value: str) -> list[int]:
    depths = sorted({int(item.strip()) for item in value.split(",") if item.strip()})
    if not depths or depths[0] <= 0:
        raise ValueError("depths must contain positive integers")
    return depths


def build_gate(
    args: argparse.Namespace, backend: Backend
) -> EvidenceStabilityGate | None:
    mode = getattr(args, "gate", "none")
    abstain_answer = getattr(args, "abstain_answer", "unknown")
    if mode == "none":
        return None
    if mode == "lexical":
        verifier = LexicalChangeVerifier(
            support_threshold=getattr(args, "gate_support_threshold", 0.8),
            margin=getattr(args, "gate_margin", 0.2),
        )
        return EvidenceStabilityGate(verifier, abstain_answer=abstain_answer)
    if mode == "never-update":
        return EvidenceStabilityGate(
            FixedDecisionVerifier("retain_previous"),
            abstain_answer=abstain_answer,
        )
    if mode == "always-abstain":
        return EvidenceStabilityGate(
            FixedDecisionVerifier("abstain"),
            abstain_answer=abstain_answer,
        )
    if mode == "model":
        complete = getattr(backend, "complete", None)
        if not callable(complete):
            raise ValueError(
                "--gate model requires a completion-capable generation backend"
            )
        return EvidenceStabilityGate(
            ModelChangeVerifier(complete),
            abstain_answer=abstain_answer,
        )
    raise ValueError(f"Unknown gate mode: {mode}")


def load_examples(path: str, limit: int | None = None) -> list[Example]:
    examples = []
    with Path(path).open(encoding="utf-8") as source:
        for line in source:
            if line.strip():
                examples.append(Example.from_dict(json.loads(line)))
    return examples[:limit] if limit else examples


def run(args: argparse.Namespace) -> None:
    backend = make_backend(args.backend, args.model, args.temperature, args.base_url)
    gate = build_gate(args, backend)
    gate_mode = getattr(args, "gate", "none")
    depths = parse_depths(args.depths)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    examples = load_examples(args.input, args.limit)

    with output.open("w", encoding="utf-8") as writer:
        for index, example in enumerate(examples, 1):
            trajectory = []
            gate_state = GateState()
            for depth in depths:
                effective_depth = min(depth, len(example.passages))
                passages = example.passages[:effective_depth]
                raw_answer = backend.answer(example.question, passages)
                step: dict[str, object] = {
                    "k": depth,
                    "effective_k": effective_depth,
                    "answer": raw_answer,
                    "correct": correctness(raw_answer, example.answers, args.scoring),
                    "f1": best_f1(raw_answer, example.answers),
                }

                if gate is not None:
                    application = gate.apply(
                        state=gate_state,
                        question=example.question,
                        passages=passages,
                        candidate_answer=raw_answer,
                    )
                    gated_correct = not application.abstained and correctness(
                        application.answer, example.answers, args.scoring
                    )
                    gate_metadata = application.to_dict()
                    gate_metadata["anchor_after"] = gate_state.anchor_answer
                    step.update(
                        {
                            "gated_answer": application.answer,
                            "gated_correct": gated_correct,
                            "gated_f1": (
                                0.0
                                if application.abstained
                                else best_f1(application.answer, example.answers)
                            ),
                            "abstained": application.abstained,
                            "gate": gate_metadata,
                        }
                    )
                trajectory.append(step)

            record = {
                "id": example.id,
                "question": example.question,
                "answers": example.answers,
                "gate_mode": gate_mode,
                "trajectory": trajectory,
            }
            writer.write(json.dumps(record, ensure_ascii=False) + "\n")
            if not args.quiet:
                print(f"{index}/{len(examples)} {example.id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--backend", choices=["mock", "openai"], default="mock")
    parser.add_argument("--model")
    parser.add_argument("--base-url", default="https://api.openai.com/v1")
    parser.add_argument("--depths", default="1,2,3,5,10")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--scoring", choices=["exact", "contains"], default="contains")
    parser.add_argument(
        "--gate",
        choices=["none", "lexical", "model", "never-update", "always-abstain"],
        default="none",
    )
    parser.add_argument("--gate-support-threshold", type=float, default=0.8)
    parser.add_argument("--gate-margin", type=float, default=0.2)
    parser.add_argument("--abstain-answer", default="unknown")
    parser.add_argument("--quiet", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()

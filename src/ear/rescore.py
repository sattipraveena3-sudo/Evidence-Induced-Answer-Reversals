from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from .scoring import best_f1, correctness


def rescore_record(record: dict[str, object], scoring: str) -> dict[str, object]:
    answers = record.get("answers")
    trajectory = record.get("trajectory")
    if not isinstance(answers, list) or not all(
        isinstance(answer, str) for answer in answers
    ):
        raise TypeError("Record answers must be a list of strings")
    if not isinstance(trajectory, list):
        raise TypeError("Record trajectory must be a list")

    for step in trajectory:
        if not isinstance(step, dict) or not isinstance(step.get("answer"), str):
            raise TypeError("Every trajectory step must contain a string answer")
        answer = step["answer"]
        step["correct"] = correctness(answer, answers, scoring)
        step["f1"] = best_f1(answer, answers)

        gated_answer = step.get("gated_answer")
        if isinstance(gated_answer, str):
            abstained = bool(step.get("abstained"))
            step["gated_correct"] = not abstained and correctness(
                gated_answer, answers, scoring
            )
            step["gated_f1"] = 0.0 if abstained else best_f1(gated_answer, answers)

    metadata = record.get("run_metadata")
    if isinstance(metadata, dict):
        metadata["scoring"] = scoring
    return record


def rescore_file(input_path: Path, output_path: Path, scoring: str) -> int:
    rows = []
    with input_path.open(encoding="utf-8") as source:
        for line in source:
            if line.strip():
                rows.append(rescore_record(json.loads(line), scoring))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as destination:
        temporary_path = Path(destination.name)
        try:
            for row in rows:
                destination.write(json.dumps(row, ensure_ascii=False) + "\n")
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
    os.replace(temporary_path, output_path)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--scoring", choices=["exact", "contains"], default="contains")
    args = parser.parse_args()
    count = rescore_file(args.input, args.output, args.scoring)
    print(f"Rescored {count} trajectories with {args.scoring} scoring")


if __name__ == "__main__":
    main()

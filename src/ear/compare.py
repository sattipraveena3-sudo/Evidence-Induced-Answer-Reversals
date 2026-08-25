from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

from .analysis import analyze_gate, bootstrap_ci, has_gate_outputs, load_jsonl


def _trajectory_depths(row: dict) -> list[int]:
    trajectory = row.get("trajectory")
    if not isinstance(trajectory, list) or not trajectory:
        raise ValueError("Every row must contain a non-empty trajectory")
    try:
        return [int(step["k"]) for step in trajectory]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Every trajectory step must contain an integer k") from exc


def _index_rows(rows: list[dict], label: str) -> tuple[list[str], dict[str, dict]]:
    if not rows:
        raise ValueError(f"{label} has no rows")
    ids: list[str] = []
    indexed: dict[str, dict] = {}
    expected_depths = _trajectory_depths(rows[0])
    for row in rows:
        identifier = row.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"Every {label} row must contain a non-empty string id")
        if identifier in indexed:
            raise ValueError(f"Duplicate {label} id: {identifier}")
        if _trajectory_depths(row) != expected_depths:
            raise ValueError(f"Inconsistent retrieval depths in {label}: {identifier}")
        ids.append(identifier)
        indexed[identifier] = row
    return ids, indexed


def _paired_metric(baseline: list[float], candidate: list[float]) -> dict[str, float]:
    if len(baseline) != len(candidate) or not baseline:
        raise ValueError("Paired metrics require equal non-empty vectors")
    differences = [new - old for old, new in zip(baseline, candidate)]
    low, high = bootstrap_ci(differences)
    return {
        "baseline": sum(baseline) / len(baseline),
        "candidate": sum(candidate) / len(candidate),
        "difference": sum(differences) / len(differences),
        "ci_low": low,
        "ci_high": high,
    }


def _correctness(row: dict) -> list[int]:
    return [int(bool(step["correct"])) for step in row["trajectory"]]


def _f1(row: dict) -> list[float]:
    return [float(step.get("f1", 0.0)) for step in row["trajectory"]]


def _reversal_profile(row: dict) -> tuple[int, int, int | None]:
    depths = _trajectory_depths(row)
    labels = [bool(value) for value in _correctness(row)]
    reversals = [
        index + 1
        for index in range(len(labels) - 1)
        if labels[index] and not labels[index + 1]
    ]
    if not reversals:
        return 0, 0, None
    first = reversals[0]
    persistent = int(all(not label for label in labels[first:]))
    return 1, persistent, depths[first]


def _event_vectors(rows: list[dict], index: int) -> tuple[list[int], list[int]]:
    ear: list[int] = []
    bcr: list[int] = []
    for row in rows:
        previous = bool(row["trajectory"][index]["correct"])
        current = bool(row["trajectory"][index + 1]["correct"])
        ear.append(int(previous and not current))
        bcr.append(int(not previous and current))
    return ear, bcr


def _gate_snapshot(rows: list[dict]) -> dict | None:
    if not has_gate_outputs(rows):
        return None
    result = analyze_gate(rows)
    return {
        "final_raw_accuracy": result["final"]["raw_accuracy"],
        "final_coverage": result["final"]["coverage"],
        "final_answered_accuracy": result["final"]["answered_accuracy"],
        "final_selective_accuracy": result["final"]["selective_accuracy"],
        "overall_raw_ear": result["overall"]["raw_ear"],
        "overall_gated_harmful": result["overall"]["gated_harmful"],
        "overall_raw_bcr": result["overall"]["raw_bcr"],
        "overall_bcr_retention": result["overall"]["bcr_retention"],
        "calls_per_example": result["verifier"]["calls_per_example"],
        "decision_counts": result["verifier"]["decision_counts"],
    }


def compare_rows(
    baseline_rows: list[dict],
    candidate_rows: list[dict],
    baseline_label: str = "baseline",
    candidate_label: str = "candidate",
) -> dict:
    baseline_ids, baseline_by_id = _index_rows(baseline_rows, "baseline")
    candidate_ids, candidate_by_id = _index_rows(candidate_rows, "candidate")
    if set(baseline_ids) != set(candidate_ids):
        missing = sorted(set(baseline_ids) - set(candidate_ids))
        extra = sorted(set(candidate_ids) - set(baseline_ids))
        raise ValueError(
            f"Question IDs differ; missing from candidate={missing}, extra={extra}"
        )
    if baseline_ids != candidate_ids:
        raise ValueError("Question IDs must appear in the same order")

    paired_baseline = [baseline_by_id[identifier] for identifier in baseline_ids]
    paired_candidate = [candidate_by_id[identifier] for identifier in baseline_ids]
    depths = _trajectory_depths(paired_baseline[0])
    if len(depths) < 2:
        raise ValueError("Paired comparison requires at least two retrieval depths")
    if _trajectory_depths(paired_candidate[0]) != depths:
        raise ValueError("Baseline and candidate retrieval depths differ")
    for identifier, old, new in zip(
        baseline_ids, paired_baseline, paired_candidate
    ):
        if _trajectory_depths(new) != depths:
            raise ValueError(f"Candidate depths differ for {identifier}")
        if old.get("question") != new.get("question"):
            raise ValueError(f"Question text differs for {identifier}")
        if old.get("answers") != new.get("answers"):
            raise ValueError(f"Reference answers differ for {identifier}")

    accuracy = []
    f1 = []
    for index, depth in enumerate(depths):
        accuracy.append(
            {
                "k": depth,
                **_paired_metric(
                    [_correctness(row)[index] for row in paired_baseline],
                    [_correctness(row)[index] for row in paired_candidate],
                ),
            }
        )
        f1.append(
            {
                "k": depth,
                **_paired_metric(
                    [_f1(row)[index] for row in paired_baseline],
                    [_f1(row)[index] for row in paired_candidate],
                ),
            }
        )

    baseline_profiles = [_reversal_profile(row) for row in paired_baseline]
    candidate_profiles = [_reversal_profile(row) for row in paired_candidate]
    baseline_any = [profile[0] for profile in baseline_profiles]
    candidate_any = [profile[0] for profile in candidate_profiles]
    baseline_persistent = [profile[1] for profile in baseline_profiles]
    candidate_persistent = [profile[1] for profile in candidate_profiles]

    membership = []
    for identifier, old, new in zip(baseline_ids, baseline_any, candidate_any):
        if old and new:
            category = "shared"
        elif old:
            category = "baseline_only"
        elif new:
            category = "candidate_only"
        else:
            category = "neither"
        membership.append(
            {
                "id": identifier,
                "baseline_any_ear": old,
                "candidate_any_ear": new,
                "category": category,
            }
        )
    category_counts = {
        category: sum(item["category"] == category for item in membership)
        for category in ("shared", "baseline_only", "candidate_only", "neither")
    }
    union = (
        category_counts["shared"]
        + category_counts["baseline_only"]
        + category_counts["candidate_only"]
    )
    baseline_frd = [profile[2] for profile in baseline_profiles if profile[2] is not None]
    candidate_frd = [profile[2] for profile in candidate_profiles if profile[2] is not None]

    transitions = []
    baseline_ear_per_question = [0.0] * len(paired_baseline)
    candidate_ear_per_question = [0.0] * len(paired_candidate)
    baseline_bcr_per_question = [0.0] * len(paired_baseline)
    candidate_bcr_per_question = [0.0] * len(paired_candidate)
    for index in range(len(depths) - 1):
        baseline_ear, baseline_bcr = _event_vectors(paired_baseline, index)
        candidate_ear, candidate_bcr = _event_vectors(paired_candidate, index)
        for row_index in range(len(paired_baseline)):
            baseline_ear_per_question[row_index] += baseline_ear[row_index]
            candidate_ear_per_question[row_index] += candidate_ear[row_index]
            baseline_bcr_per_question[row_index] += baseline_bcr[row_index]
            candidate_bcr_per_question[row_index] += candidate_bcr[row_index]
        transitions.append(
            {
                "from_k": depths[index],
                "to_k": depths[index + 1],
                "ear": _paired_metric(baseline_ear, candidate_ear),
                "bcr": _paired_metric(baseline_bcr, candidate_bcr),
            }
        )
    transition_count = len(depths) - 1
    for values in (
        baseline_ear_per_question,
        candidate_ear_per_question,
        baseline_bcr_per_question,
        candidate_bcr_per_question,
    ):
        for index, value in enumerate(values):
            values[index] = value / transition_count

    return {
        "schema_version": 1,
        "n": len(baseline_ids),
        "depths": depths,
        "baseline_label": baseline_label,
        "candidate_label": candidate_label,
        "accuracy": accuracy,
        "f1": f1,
        "trajectories": {
            "ear_at_k": _paired_metric(baseline_any, candidate_any),
            "persistent_ear": _paired_metric(
                baseline_persistent, candidate_persistent
            ),
            "median_first_reversal_depth": {
                "baseline": statistics.median(baseline_frd)
                if baseline_frd
                else None,
                "candidate": statistics.median(candidate_frd)
                if candidate_frd
                else None,
            },
            "reversal_sets": {
                **category_counts,
                "jaccard": category_counts["shared"] / union if union else 1.0,
            },
        },
        "transitions": transitions,
        "overall_transitions": {
            "ear": _paired_metric(
                baseline_ear_per_question, candidate_ear_per_question
            ),
            "bcr": _paired_metric(
                baseline_bcr_per_question, candidate_bcr_per_question
            ),
            "bootstrap_unit": "question trajectory",
        },
        "gate": {
            "baseline": _gate_snapshot(paired_baseline),
            "candidate": _gate_snapshot(paired_candidate),
        },
        "reversal_membership": membership,
    }


def _comparison_rows(result: dict) -> list[dict]:
    rows = []

    def add(category: str, metric: str, location: str, values: dict) -> None:
        rows.append(
            {
                "category": category,
                "metric": metric,
                "location": location,
                **values,
            }
        )

    for metric in ("accuracy", "f1"):
        for values in result[metric]:
            add(metric, metric, f"k={values['k']}", {k: v for k, v in values.items() if k != "k"})
    add("trajectory", "EAR@K", f"k={max(result['depths'])}", result["trajectories"]["ear_at_k"])
    add("trajectory", "P-EAR", f"k={max(result['depths'])}", result["trajectories"]["persistent_ear"])
    for transition in result["transitions"]:
        location = f"{transition['from_k']}->{transition['to_k']}"
        add("transition", "EAR", location, transition["ear"])
        add("transition", "BCR", location, transition["bcr"])
    add("overall_transition", "EAR", "all adjacent", result["overall_transitions"]["ear"])
    add("overall_transition", "BCR", "all adjacent", result["overall_transitions"]["bcr"])
    return rows


def write_comparison(result: dict, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    serializable = {key: value for key, value in result.items() if key != "reversal_membership"}
    (outdir / "comparison.json").write_text(
        json.dumps(serializable, indent=2), encoding="utf-8"
    )
    rows = _comparison_rows(result)
    with (outdir / "comparison.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    with (outdir / "reversal_set_membership.csv").open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.DictWriter(
            output,
            fieldnames=["id", "baseline_any_ear", "candidate_any_ear", "category"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result["reversal_membership"])


def make_plots(result: dict, outdir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping comparison plots")
        return

    depths = result["depths"]
    baseline = [item["baseline"] for item in result["accuracy"]]
    candidate = [item["candidate"] for item in result["accuracy"]]
    fig = plt.figure(figsize=(7.2, 4.5))
    plt.plot(depths, baseline, marker="o", label=result["baseline_label"])
    plt.plot(depths, candidate, marker="o", label=result["candidate_label"])
    plt.xlabel("Retrieval depth k")
    plt.ylabel("Accuracy")
    plt.title("Paired accuracy by model scale")
    plt.xticks(depths)
    plt.ylim(0, 1)
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    fig.savefig(outdir / "paired_accuracy_by_k.png", dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paired comparison of two answer-trajectory conditions."
    )
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args()
    result = compare_rows(
        load_jsonl(args.baseline),
        load_jsonl(args.candidate),
        baseline_label=args.baseline_label,
        candidate_label=args.candidate_label,
    )
    write_comparison(result, args.outdir)
    if args.plots:
        make_plots(result, args.outdir)
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "reversal_membership"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

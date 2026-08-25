import csv
import json

import pytest

from ear.compare import compare_rows, write_comparison


def _row(identifier, labels, f1=None, question=None):
    depths = [1, 2, 3]
    return {
        "id": identifier,
        "question": question or f"Question {identifier}",
        "answers": [f"Answer {identifier}"],
        "trajectory": [
            {
                "k": depth,
                "correct": label,
                "f1": score,
            }
            for depth, label, score in zip(depths, labels, f1 or labels)
        ],
    }


def test_compare_rows_computes_paired_scale_metrics():
    baseline = [
        _row("a", [True, False, False]),
        _row("b", [False, True, True]),
        _row("c", [True, True, True]),
        _row("d", [False, False, False]),
    ]
    candidate = [
        _row("a", [True, True, True]),
        _row("b", [False, True, False]),
        _row("c", [True, False, True]),
        _row("d", [False, False, False]),
    ]

    result = compare_rows(baseline, candidate, "0.5B", "1.5B")

    assert result["n"] == 4
    assert result["accuracy"][1]["baseline"] == 0.5
    assert result["accuracy"][1]["candidate"] == 0.5
    assert result["trajectories"]["ear_at_k"]["baseline"] == 0.25
    assert result["trajectories"]["ear_at_k"]["candidate"] == 0.5
    assert result["trajectories"]["ear_at_k"]["difference"] == 0.25
    sets = result["trajectories"]["reversal_sets"]
    assert sets == {
        "shared": 0,
        "baseline_only": 1,
        "candidate_only": 2,
        "neither": 1,
        "jaccard": 0.0,
    }
    assert result["overall_transitions"]["ear"]["baseline"] == 0.125
    assert result["overall_transitions"]["ear"]["candidate"] == 0.25
    assert result["overall_transitions"]["bcr"]["baseline"] == 0.125
    assert result["overall_transitions"]["bcr"]["candidate"] == 0.25


def test_compare_rows_rejects_nonidentical_pairing():
    baseline = [_row("a", [True, True, True]), _row("b", [False, False, False])]
    reordered = [baseline[1], baseline[0]]
    with pytest.raises(ValueError, match="same order"):
        compare_rows(baseline, reordered)

    changed = [_row("a", [True, True, True], question="Changed"), baseline[1]]
    with pytest.raises(ValueError, match="Question text differs"):
        compare_rows(baseline, changed)


def test_write_comparison_outputs_machine_readable_tables(tmp_path):
    rows = [_row("a", [True, False, False]), _row("b", [False, True, True])]
    result = compare_rows(rows, rows)
    write_comparison(result, tmp_path)

    payload = json.loads((tmp_path / "comparison.json").read_text(encoding="utf-8"))
    assert payload["n"] == 2
    assert "reversal_membership" not in payload
    with (tmp_path / "comparison.csv").open(encoding="utf-8") as source:
        assert any(row["metric"] == "EAR@K" for row in csv.DictReader(source))
    with (tmp_path / "reversal_set_membership.csv").open(encoding="utf-8") as source:
        membership = list(csv.DictReader(source))
    assert membership[0]["category"] == "shared"

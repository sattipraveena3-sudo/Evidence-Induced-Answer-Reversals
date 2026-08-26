from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONDITIONS = {
    "pilot_qwen2_5_0_5b_hotpotqa_100": {
        "ear_at_k": 0.23,
        "p_ear": 0.12,
        "raw_ear": 0.0625,
        "gated_harmful": 0.0025,
        "bcr_retention": 0.411764705882353,
        "raw_accuracy": 0.32,
        "coverage": 0.55,
        "answered_accuracy": 0.22,
    },
    "replication_qwen2_5_1_5b_hotpotqa_100": {
        "ear_at_k": 0.22,
        "p_ear": 0.13,
        "raw_ear": 0.0575,
        "gated_harmful": 0.005,
        "bcr_retention": 0.2926829268292683,
        "raw_accuracy": 0.40,
        "coverage": 0.61,
        "answered_accuracy": 0.22,
    },
    "replication_smollm2_1_7b_hotpotqa_100": {
        "ear_at_k": 0.32,
        "p_ear": 0.21,
        "raw_ear": 0.09,
        "gated_harmful": 0.0025,
        "bcr_retention": 0.41379310344827586,
        "raw_accuracy": 0.18,
        "coverage": 0.52,
        "answered_accuracy": 0.17,
    },
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_literature_matrix_has_30_unique_primary_sources() -> None:
    matrix_path = ROOT / "paper" / "LITERATURE_MATRIX.csv"
    with matrix_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 30
    assert len({row["id"] for row in rows}) == 30
    assert all(row["url"].startswith("https://") for row in rows)
    assert {row["category"] for row in rows} == {
        "Foundations",
        "Robustness",
        "Evaluation",
        "Mitigation",
    }


def test_every_manuscript_citation_resolves() -> None:
    manuscript = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")
    bibliography = (ROOT / "paper" / "references.bib").read_text(
        encoding="utf-8"
    )
    bib_keys = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bibliography))
    cited_keys = {
        key.strip()
        for group in re.findall(r"\\cite[tp]?\{([^}]+)\}", manuscript)
        for key in group.split(",")
    }

    assert len(bib_keys) == 32  # 30 mapped papers plus two model reports.
    assert cited_keys == bib_keys


def test_core_paper_metrics_match_committed_results() -> None:
    for condition, expected in CONDITIONS.items():
        result_dir = ROOT / "results" / condition
        summary = load_json(result_dir / "summary.json")
        gate = load_json(result_dir / "gate_summary.json")

        assert summary["ear_at_k"] == expected["ear_at_k"]
        assert summary["p_ear"] == expected["p_ear"]
        assert gate["overall"]["raw_ear"] == expected["raw_ear"]
        assert gate["overall"]["gated_harmful"] == expected["gated_harmful"]
        assert gate["overall"]["bcr_retention"] == expected["bcr_retention"]
        assert gate["final"]["raw_accuracy"] == expected["raw_accuracy"]
        assert gate["final"]["coverage"] == expected["coverage"]
        assert gate["final"]["answered_accuracy"] == expected["answered_accuracy"]

        accuracy = {row["k"]: row["accuracy"] for row in summary["accuracy"]}
        for transition in summary["transitions"]:
            observed_delta = (
                accuracy[transition["to_k"]] - accuracy[transition["from_k"]]
            )
            expected_delta = transition["bcr"] - transition["ear"]
            assert abs(observed_delta - expected_delta) < 1e-12


def test_final_manuscript_pdf_and_figure_are_present() -> None:
    pdf = (
        ROOT
        / "output"
        / "pdf"
        / "Evidence_Induced_Answer_Reversals_Praveena_Satti.pdf"
    )
    figure = ROOT / "paper" / "figures" / "main_results.png"

    assert pdf.read_bytes().startswith(b"%PDF-")
    assert pdf.stat().st_size > 100_000
    assert figure.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert figure.stat().st_size > 100_000

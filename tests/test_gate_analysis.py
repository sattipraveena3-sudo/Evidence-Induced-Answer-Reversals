from ear.analysis import analyze, analyze_gate, write_outputs


def _gate(triggered, decision):
    return {
        "triggered": triggered,
        "decision": decision,
        "latency_ms": 2.0 if triggered else 0.0,
    }


def test_gate_analysis_separates_harm_from_abstention(tmp_path):
    rows = [
        {
            "gate_mode": "lexical",
            "trajectory": [
                {
                    "k": 1,
                    "correct": True,
                    "f1": 1.0,
                    "gated_correct": True,
                    "abstained": False,
                    "gate": _gate(False, "initial"),
                },
                {
                    "k": 3,
                    "correct": False,
                    "f1": 0.0,
                    "gated_correct": False,
                    "abstained": True,
                    "gate": _gate(True, "abstain"),
                },
            ],
        },
        {
            "gate_mode": "lexical",
            "trajectory": [
                {
                    "k": 1,
                    "correct": False,
                    "f1": 0.0,
                    "gated_correct": False,
                    "abstained": False,
                    "gate": _gate(False, "initial"),
                },
                {
                    "k": 3,
                    "correct": True,
                    "f1": 1.0,
                    "gated_correct": True,
                    "abstained": False,
                    "gate": _gate(True, "accept_new"),
                },
            ],
        },
    ]

    result = analyze_gate(rows)
    transition = result["transitions"][0]
    assert transition["raw_ear"] == 0.5
    assert transition["raw_ear_gated_abstain"] == 0.5
    assert transition["raw_ear_gated_incorrect"] == 0.0
    assert transition["gated_harmful"] == 0.0
    assert transition["correct_to_abstain"] == 0.5
    assert transition["raw_bcr"] == 0.5
    assert transition["bcr_retained"] == 0.5
    assert transition["gated_bcr"] == 0.5
    assert result["overall"]["bcr_retention"] == 1.0
    assert result["final"]["coverage"] == 0.5
    assert result["final"]["selective_accuracy"] == 1.0
    assert result["verifier"]["calls"] == 2

    write_outputs(analyze(rows), tmp_path, rows=rows)
    assert (tmp_path / "gate_summary.json").is_file()
    assert (tmp_path / "gate_depth_metrics.csv").is_file()
    assert (tmp_path / "gate_transitions.csv").is_file()
    assert (tmp_path / "gate_decisions.csv").is_file()

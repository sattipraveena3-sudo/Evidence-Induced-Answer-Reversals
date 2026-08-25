import json

from ear.rescore import rescore_file


def test_rescore_corrects_substring_labels_and_supports_in_place_update(tmp_path):
    path = tmp_path / "trajectories.jsonl"
    row = {
        "answers": ["no"],
        "run_metadata": {"scoring": "contains"},
        "trajectory": [
            {
                "answer": "unknown",
                "correct": True,
                "f1": 0.0,
                "gated_answer": "No.",
                "gated_correct": False,
                "gated_f1": 0.0,
                "abstained": False,
            }
        ],
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    assert rescore_file(path, path, "contains") == 1

    rescored = json.loads(path.read_text(encoding="utf-8"))
    step = rescored["trajectory"][0]
    assert not step["correct"]
    assert step["gated_correct"]
    assert step["gated_f1"] == 1.0

from ear.analysis import analyze

def test_ear_bcr_identity():
    rows = [
        {"trajectory": [{"k": 1, "correct": True, "f1": 1}, {"k": 3, "correct": False, "f1": 0}]},
        {"trajectory": [{"k": 1, "correct": False, "f1": 0}, {"k": 3, "correct": True, "f1": 1}]},
        {"trajectory": [{"k": 1, "correct": True, "f1": 1}, {"k": 3, "correct": True, "f1": 1}]},
        {"trajectory": [{"k": 1, "correct": False, "f1": 0}, {"k": 3, "correct": False, "f1": 0}]},
    ]
    r = analyze(rows)
    t = r["transitions"][0]
    assert t["ear"] == 0.25
    assert t["bcr"] == 0.25
    assert abs(t["rtb"]) < 1e-12
    a1 = r["accuracy"][0]["accuracy"]
    a3 = r["accuracy"][1]["accuracy"]
    assert abs((a3 - a1) - t["rtb"]) < 1e-12

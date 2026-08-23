from ear.scoring import normalize_answer, exact_match, best_f1

def test_normalization():
    assert normalize_answer("The, Eiffel Tower!") == "eiffel tower"

def test_em():
    assert exact_match("Franz Kafka", ["Kafka", "Franz Kafka"])

def test_f1():
    assert best_f1("Franz Kafka", ["Kafka"]) > 0

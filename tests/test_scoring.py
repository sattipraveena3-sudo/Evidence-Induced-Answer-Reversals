from ear.scoring import best_f1, contains_match, exact_match, normalize_answer


def test_normalization():
    assert normalize_answer("The, Eiffel Tower!") == "eiffel tower"


def test_em():
    assert exact_match("Franz Kafka", ["Kafka", "Franz Kafka"])


def test_f1():
    assert best_f1("Franz Kafka", ["Kafka"]) > 0


def test_contains_uses_whole_token_sequences_not_substrings():
    assert contains_match("The answer is New York City.", ["New York"])
    assert not contains_match("unknown", ["no"])
    assert not contains_match("both operas", ["an opera"])

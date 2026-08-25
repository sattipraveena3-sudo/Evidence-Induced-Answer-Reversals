from __future__ import annotations

import re
import string
from collections import Counter


def normalize_answer(s: str) -> str:
    s = s.lower().strip()
    s = "".join(ch for ch in s if ch not in string.punctuation)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def exact_match(pred: str, golds: list[str]) -> bool:
    p = normalize_answer(pred)
    return any(p == normalize_answer(g) for g in golds)


def contains_token_sequence(pred_tokens: list[str], gold_tokens: list[str]) -> bool:
    if not gold_tokens or len(gold_tokens) > len(pred_tokens):
        return False
    width = len(gold_tokens)
    return any(
        pred_tokens[start : start + width] == gold_tokens
        for start in range(len(pred_tokens) - width + 1)
    )


def contains_match(pred: str, golds: list[str]) -> bool:
    pred_tokens = normalize_answer(pred).split()
    return any(
        contains_token_sequence(pred_tokens, normalize_answer(gold).split())
        for gold in golds
    )


def token_f1_single(pred: str, gold: str) -> float:
    p = normalize_answer(pred).split()
    g = normalize_answer(gold).split()
    if not p and not g:
        return 1.0
    if not p or not g:
        return 0.0
    common = Counter(p) & Counter(g)
    overlap = sum(common.values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(p)
    recall = overlap / len(g)
    return 2 * precision * recall / (precision + recall)


def best_f1(pred: str, golds: list[str]) -> float:
    return max(token_f1_single(pred, g) for g in golds)


def correctness(pred: str, golds: list[str], mode: str = "contains") -> bool:
    if mode == "exact":
        return exact_match(pred, golds)
    if mode == "contains":
        return contains_match(pred, golds)
    raise ValueError(f"Unknown scoring mode: {mode}")

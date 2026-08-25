from __future__ import annotations

import argparse
import json
import random
import re
import urllib.request
from collections import Counter
from pathlib import Path

SOURCES = [
    "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json",
    "https://huggingface.co/datasets/namlh2004/hotpotqa/resolve/7e54db4656209750ff487f6fdf8e39a66dba136b/hotpot_dev_distractor_v1.json?download=true",
]


def tok(s: str):
    return re.findall(r"[a-z0-9]+", s.lower())


def lexical_rank(question: str, paragraphs: list[tuple[str, list[str]]]):
    q = Counter(tok(question))
    scored = []
    for idx, (title, sents) in enumerate(paragraphs):
        text = title + " " + " ".join(sents)
        d = Counter(tok(text))
        overlap = sum(min(q[t], d[t]) for t in q)
        title_overlap = sum(1 for t in set(tok(title)) if t in q)
        score = 3 * title_overlap + overlap + 0.001 * (len(paragraphs) - idx)
        scored.append((score, idx, text))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [x[2] for x in scored]


def download_dataset():
    last_error = None
    for url in SOURCES:
        try:
            print(f"Downloading HotpotQA from {url}")
            req = urllib.request.Request(
                url, headers={"User-Agent": "ear-rag-research/0.1"}
            )
            with urllib.request.urlopen(req, timeout=240) as r:
                payload = r.read()
            data = json.loads(payload.decode("utf-8"))
            print(f"Downloaded {len(data)} HotpotQA examples")
            return data
        except (OSError, TimeoutError, ValueError) as exc:
            print(f"HotpotQA source failed: {exc}")
            last_error = exc
    raise RuntimeError(f"All HotpotQA download sources failed: {last_error}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="data/primary.jsonl")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    data = download_dataset()
    rng = random.Random(args.seed)
    rng.shuffle(data)
    data = data[: args.limit]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as w:
        for ex in data:
            passages = lexical_rank(ex["question"], ex["context"])
            rec = {
                "id": ex["_id"],
                "question": ex["question"],
                "answers": [ex["answer"]],
                "passages": passages,
                "source": "HotpotQA dev distractor",
                "ranking": "deterministic lexical-overlap baseline",
            }
            w.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(data)} questions to {out}")


if __name__ == "__main__":
    main()

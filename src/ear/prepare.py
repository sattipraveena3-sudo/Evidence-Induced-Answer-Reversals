from __future__ import annotations
import argparse, json, csv
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description="Convert CSV to EAR JSONL.")
    p.add_argument("--csv", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--id-col", default="id")
    p.add_argument("--question-col", default="question")
    p.add_argument("--answer-col", default="answer")
    p.add_argument("--passage-prefix", default="passage_")
    a = p.parse_args()
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.csv, newline="", encoding="utf-8") as f, out.open("w", encoding="utf-8") as w:
        for row in csv.DictReader(f):
            passage_cols = sorted([k for k in row if k.startswith(a.passage_prefix)], key=lambda x: int(x[len(a.passage_prefix):]))
            rec = {
                "id": row[a.id_col],
                "question": row[a.question_col],
                "answers": [row[a.answer_col]],
                "passages": [row[k] for k in passage_cols if row[k].strip()]
            }
            w.write(json.dumps(rec, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()

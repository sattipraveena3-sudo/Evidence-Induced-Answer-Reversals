from __future__ import annotations
import argparse, json
from pathlib import Path
from .schema import Example
from .backends import make_backend
from .scoring import correctness, best_f1

def parse_depths(s: str) -> list[int]:
    vals = sorted(set(int(x.strip()) for x in s.split(",") if x.strip()))
    if not vals or vals[0] <= 0:
        raise ValueError("depths must contain positive integers")
    return vals

def run(args):
    backend = make_backend(args.backend, args.model, args.temperature, args.base_url)
    depths = parse_depths(args.depths)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    examples = []
    with open(args.input, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(Example.from_dict(json.loads(line)))
    if args.limit:
        examples = examples[:args.limit]
    with out.open("w", encoding="utf-8") as w:
        for idx, ex in enumerate(examples, 1):
            traj = []
            for k in depths:
                use_k = min(k, len(ex.passages))
                pred = backend.answer(ex.question, ex.passages[:use_k])
                traj.append({
                    "k": k,
                    "effective_k": use_k,
                    "answer": pred,
                    "correct": correctness(pred, ex.answers, args.scoring),
                    "f1": best_f1(pred, ex.answers),
                })
            rec = {"id": ex.id, "question": ex.question, "answers": ex.answers, "trajectory": traj}
            w.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if not args.quiet:
                print(f"{idx}/{len(examples)} {ex.id}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--backend", choices=["mock", "openai"], default="mock")
    p.add_argument("--model")
    p.add_argument("--base-url", default="https://api.openai.com/v1")
    p.add_argument("--depths", default="1,2,3,5,10")
    p.add_argument("--limit", type=int)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--scoring", choices=["exact", "contains"], default="contains")
    p.add_argument("--quiet", action="store_true")
    run(p.parse_args())

if __name__ == "__main__":
    main()

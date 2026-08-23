from __future__ import annotations
import argparse, json, csv, random, statistics
from pathlib import Path
from collections import Counter

def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def bootstrap_ci(vals, B=3000, seed=7):
    if not vals:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(vals)
    means = []
    for _ in range(B):
        means.append(sum(vals[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return means[int(.025 * B)], means[min(B - 1, int(.975 * B))]

def trajectory_label(ys):
    if all(ys):
        return "stable_correct"
    if not any(ys):
        return "persistent_failure"
    rev = any(ys[i] and not ys[i + 1] for i in range(len(ys) - 1))
    corr = any((not ys[i]) and ys[i + 1] for i in range(len(ys) - 1))
    if rev and corr:
        changes = sum(ys[i] != ys[i + 1] for i in range(len(ys) - 1))
        return "oscillation" if changes >= 3 else "temporary_reversal"
    if rev:
        return "harmful_reversal"
    if corr:
        return "beneficial_recovery"
    return "mixed"

def analyze(rows):
    if not rows:
        raise ValueError("No rows")
    depths = [t["k"] for t in rows[0]["trajectory"]]
    n = len(rows)
    accuracy = []
    f1s = []
    for j, k in enumerate(depths):
        ys = [int(r["trajectory"][j]["correct"]) for r in rows]
        fs = [float(r["trajectory"][j].get("f1", 0.0)) for r in rows]
        lo, hi = bootstrap_ci(ys)
        accuracy.append({"k": k, "accuracy": sum(ys) / n, "ci_low": lo, "ci_high": hi})
        f1s.append({"k": k, "f1": sum(fs) / n})

    transitions = []
    for j in range(len(depths) - 1):
        ear = []
        bcr = []
        for r in rows:
            a = bool(r["trajectory"][j]["correct"])
            b = bool(r["trajectory"][j + 1]["correct"])
            ear.append(int(a and not b))
            bcr.append(int((not a) and b))
        elo, ehi = bootstrap_ci(ear)
        blo, bhi = bootstrap_ci(bcr)
        e = sum(ear) / n
        b = sum(bcr) / n
        transitions.append({
            "from_k": depths[j], "to_k": depths[j + 1],
            "ear": e, "ear_ci_low": elo, "ear_ci_high": ehi,
            "bcr": b, "bcr_ci_low": blo, "bcr_ci_high": bhi,
            "rtb": b - e
        })

    any_ear, persistent, frd, examples = [], [], [], []
    labels = Counter()
    for r in rows:
        ys = [bool(t["correct"]) for t in r["trajectory"]]
        labels[trajectory_label(ys)] += 1
        rev = [i + 1 for i in range(len(ys) - 1) if ys[i] and not ys[i + 1]]
        any_ear.append(int(bool(rev)))
        if rev:
            first = rev[0]
            frd.append(depths[first])
            persistent.append(int(all(not y for y in ys[first:])))
            examples.append(r)
        else:
            persistent.append(0)

    ear_at_k = sum(any_ear) / n
    p_ear = sum(persistent) / n
    return {
        "n": n,
        "depths": depths,
        "accuracy": accuracy,
        "f1": f1s,
        "transitions": transitions,
        "ear_at_k": ear_at_k,
        "ear_at_k_ci": bootstrap_ci(any_ear),
        "p_ear": p_ear,
        "p_ear_ci": bootstrap_ci(persistent),
        "median_frd": statistics.median(frd) if frd else None,
        "trajectory_counts": dict(labels),
        "reversal_examples": examples,
    }

def write_outputs(res, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    safe = {k: v for k, v in res.items() if k != "reversal_examples"}
    (outdir / "summary.json").write_text(json.dumps(safe, indent=2), encoding="utf-8")
    with (outdir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "k_or_transition", "value", "ci_low", "ci_high"])
        for a in res["accuracy"]:
            w.writerow(["accuracy", a["k"], a["accuracy"], a["ci_low"], a["ci_high"]])
        w.writerow(["EAR@K", max(res["depths"]), res["ear_at_k"], *res["ear_at_k_ci"]])
        w.writerow(["P-EAR", max(res["depths"]), res["p_ear"], *res["p_ear_ci"]])
    with (outdir / "transitions.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["from_k", "to_k", "ear", "ear_ci_low", "ear_ci_high", "bcr", "bcr_ci_low", "bcr_ci_high", "rtb"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(res["transitions"])
    with (outdir / "trajectory_counts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["trajectory_type", "count"])
        for k, v in sorted(res["trajectory_counts"].items()):
            w.writerow([k, v])
    with (outdir / "reversal_examples.jsonl").open("w", encoding="utf-8") as f:
        for r in res["reversal_examples"]:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def make_plots(res, outdir: Path):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not installed; skipping plots")
        return
    ks = [x["k"] for x in res["accuracy"]]
    vals = [x["accuracy"] for x in res["accuracy"]]
    fig = plt.figure()
    plt.plot(ks, vals, marker="o")
    plt.xlabel("Retrieval depth k")
    plt.ylabel("Accuracy")
    plt.title("Accuracy across retrieval depth")
    plt.tight_layout()
    fig.savefig(outdir / "accuracy_by_k.png", dpi=200)
    plt.close(fig)
    labels = [f'{x["from_k"]}→{x["to_k"]}' for x in res["transitions"]]
    ear = [x["ear"] for x in res["transitions"]]
    bcr = [x["bcr"] for x in res["transitions"]]
    fig = plt.figure()
    x = range(len(labels))
    plt.plot(x, ear, marker="o", label="EAR")
    plt.plot(x, bcr, marker="o", label="BCR")
    plt.xticks(list(x), labels)
    plt.xlabel("Retrieval-depth transition")
    plt.ylabel("Rate")
    plt.title("Harmful reversals vs beneficial corrections")
    plt.legend()
    plt.tight_layout()
    fig.savefig(outdir / "ear_bcr_by_transition.png", dpi=200)
    plt.close(fig)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--plots", action="store_true")
    a = p.parse_args()
    res = analyze(load_jsonl(a.input))
    out = Path(a.outdir)
    write_outputs(res, out)
    if a.plots:
        make_plots(res, out)
    print(json.dumps({k: v for k, v in res.items() if k != "reversal_examples"}, indent=2))

if __name__ == "__main__":
    main()

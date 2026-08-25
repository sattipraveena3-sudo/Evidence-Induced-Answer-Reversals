from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from collections import Counter
from pathlib import Path


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
    return means[int(0.025 * B)], means[min(B - 1, int(0.975 * B))]


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
        transitions.append(
            {
                "from_k": depths[j],
                "to_k": depths[j + 1],
                "ear": e,
                "ear_ci_low": elo,
                "ear_ci_high": ehi,
                "bcr": b,
                "bcr_ci_low": blo,
                "bcr_ci_high": bhi,
                "rtb": b - e,
            }
        )

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


def has_gate_outputs(rows):
    return all(
        "gated_correct" in step and "abstained" in step and "gate" in step
        for row in rows
        for step in row["trajectory"]
    )


def _rate(values):
    return sum(values) / len(values) if values else 0.0


def _metric_with_ci(values):
    low, high = bootstrap_ci(values)
    return _rate(values), low, high


def analyze_gate(rows):
    """Compare raw transitions with selective, stateful gate outcomes.

    Abstentions are reported separately rather than being relabeled as incorrect
    answers. This prevents an apparent EAR reduction from hiding lost coverage.
    """

    if not rows:
        raise ValueError("No rows")
    if not has_gate_outputs(rows):
        raise ValueError("Rows do not contain gate outputs")

    depths = [step["k"] for step in rows[0]["trajectory"]]
    if len(depths) < 2:
        raise ValueError("Gate analysis requires at least two retrieval depths")
    n = len(rows)
    depth_metrics = []
    for index, depth in enumerate(depths):
        steps = [row["trajectory"][index] for row in rows]
        coverage_values = [int(not step["abstained"]) for step in steps]
        correct_values = [
            int(not step["abstained"] and step["gated_correct"]) for step in steps
        ]
        answered = sum(coverage_values)
        depth_metrics.append(
            {
                "k": depth,
                "raw_accuracy": _rate([int(step["correct"]) for step in steps]),
                "coverage": _rate(coverage_values),
                "answered_accuracy": _rate(correct_values),
                "selective_accuracy": sum(correct_values) / answered
                if answered
                else None,
            }
        )

    transitions = []
    aggregate = {
        "raw_ear": [],
        "raw_ear_gated_incorrect": [],
        "raw_ear_gated_abstain": [],
        "raw_ear_gated_correct": [],
        "gated_harmful": [],
        "raw_bcr": [],
        "bcr_retained": [],
        "gated_bcr": [],
        "correct_to_abstain": [],
        "abstain_to_correct": [],
    }
    for index in range(len(depths) - 1):
        indicators = {name: [] for name in aggregate}
        for row in rows:
            previous = row["trajectory"][index]
            current = row["trajectory"][index + 1]
            previous_answered = not bool(previous["abstained"])
            current_answered = not bool(current["abstained"])
            previous_gated_correct = bool(previous["gated_correct"])
            current_gated_correct = bool(current["gated_correct"])

            raw_ear = bool(previous["correct"]) and not bool(current["correct"])
            raw_bcr = not bool(previous["correct"]) and bool(current["correct"])
            indicators["raw_ear"].append(int(raw_ear))
            indicators["raw_ear_gated_incorrect"].append(
                int(raw_ear and current_answered and not current_gated_correct)
            )
            indicators["raw_ear_gated_abstain"].append(
                int(raw_ear and not current_answered)
            )
            indicators["raw_ear_gated_correct"].append(
                int(raw_ear and current_answered and current_gated_correct)
            )
            indicators["raw_bcr"].append(int(raw_bcr))
            indicators["bcr_retained"].append(
                int(raw_bcr and current_answered and current_gated_correct)
            )
            indicators["gated_harmful"].append(
                int(
                    previous_answered
                    and previous_gated_correct
                    and current_answered
                    and not current_gated_correct
                )
            )
            indicators["gated_bcr"].append(
                int(
                    previous_answered
                    and not previous_gated_correct
                    and current_answered
                    and current_gated_correct
                )
            )
            indicators["correct_to_abstain"].append(
                int(
                    previous_answered
                    and previous_gated_correct
                    and not current_answered
                )
            )
            indicators["abstain_to_correct"].append(
                int(
                    not previous_answered and current_answered and current_gated_correct
                )
            )

        transition = {"from_k": depths[index], "to_k": depths[index + 1]}
        for name, values in indicators.items():
            value, low, high = _metric_with_ci(values)
            transition[name] = value
            transition[f"{name}_ci_low"] = low
            transition[f"{name}_ci_high"] = high
            aggregate[name].extend(values)
        transitions.append(transition)

    triggered = []
    latencies = []
    decisions = Counter()
    for row in rows:
        for step in row["trajectory"]:
            gate = step["gate"]
            decisions[str(gate["decision"])] += 1
            if gate["triggered"]:
                triggered.append(1)
                latencies.append(float(gate.get("latency_ms", 0.0)))

    raw_ear = _rate(aggregate["raw_ear"])
    gated_harmful = _rate(aggregate["gated_harmful"])
    raw_bcr = _rate(aggregate["raw_bcr"])
    bcr_retained = _rate(aggregate["bcr_retained"])
    gated_bcr = _rate(aggregate["gated_bcr"])
    opportunities = n * max(0, len(depths) - 1)
    final = depth_metrics[-1]

    return {
        "n": n,
        "depths": depths,
        "gate_mode": rows[0].get("gate_mode", "unknown"),
        "depth_metrics": depth_metrics,
        "transitions": transitions,
        "overall": {
            "raw_ear": raw_ear,
            "raw_ear_gated_incorrect": _rate(aggregate["raw_ear_gated_incorrect"]),
            "raw_ear_gated_abstain": _rate(aggregate["raw_ear_gated_abstain"]),
            "raw_ear_gated_correct": _rate(aggregate["raw_ear_gated_correct"]),
            "gated_harmful": gated_harmful,
            "ear_reduction_absolute": raw_ear - gated_harmful,
            "ear_reduction_relative": (
                (raw_ear - gated_harmful) / raw_ear if raw_ear else None
            ),
            "raw_bcr": raw_bcr,
            "bcr_retained": bcr_retained,
            "gated_bcr": gated_bcr,
            "bcr_retention": bcr_retained / raw_bcr if raw_bcr else None,
            "correct_to_abstain": _rate(aggregate["correct_to_abstain"]),
            "abstain_to_correct": _rate(aggregate["abstain_to_correct"]),
        },
        "final": {
            "k": final["k"],
            "raw_accuracy": final["raw_accuracy"],
            "coverage": final["coverage"],
            "answered_accuracy": final["answered_accuracy"],
            "selective_accuracy": final["selective_accuracy"],
        },
        "verifier": {
            "calls": len(triggered),
            "calls_per_example": len(triggered) / n,
            "call_rate_per_transition": len(triggered) / opportunities
            if opportunities
            else 0.0,
            "mean_latency_ms": statistics.mean(latencies) if latencies else 0.0,
            "decision_counts": dict(decisions),
        },
    }


def write_gate_outputs(res, outdir: Path):
    (outdir / "gate_summary.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8"
    )
    with (outdir / "gate_depth_metrics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(res["depth_metrics"][0]))
        writer.writeheader()
        writer.writerows(res["depth_metrics"])
    with (outdir / "gate_transitions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(res["transitions"][0]))
        writer.writeheader()
        writer.writerows(res["transitions"])
    with (outdir / "gate_decisions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["decision", "count"])
        for decision, count in sorted(res["verifier"]["decision_counts"].items()):
            writer.writerow([decision, count])


def write_outputs(res, outdir: Path, rows=None):
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
        fields = [
            "from_k",
            "to_k",
            "ear",
            "ear_ci_low",
            "ear_ci_high",
            "bcr",
            "bcr_ci_low",
            "bcr_ci_high",
            "rtb",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(res["transitions"])
    with (outdir / "trajectory_counts.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.writer(f)
        w.writerow(["trajectory_type", "count"])
        for k, v in sorted(res["trajectory_counts"].items()):
            w.writerow([k, v])
    with (outdir / "reversal_examples.jsonl").open("w", encoding="utf-8") as f:
        for r in res["reversal_examples"]:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    gate_res = (
        analyze_gate(rows) if rows is not None and has_gate_outputs(rows) else None
    )
    if gate_res is not None:
        write_gate_outputs(gate_res, outdir)
    return gate_res


def make_plots(res, outdir: Path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
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
    labels = [f"{x['from_k']}→{x['to_k']}" for x in res["transitions"]]
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
    rows = load_jsonl(a.input)
    res = analyze(rows)
    out = Path(a.outdir)
    gate_res = write_outputs(res, out, rows=rows)
    if a.plots:
        make_plots(res, out)
    payload = {"raw": {k: v for k, v in res.items() if k != "reversal_examples"}}
    if gate_res is not None:
        payload["gate"] = gate_res
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

"""Build the manuscript figure directly from committed experiment summaries."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"

CONDITIONS = [
    (
        "Qwen 0.5B",
        ROOT / "results" / "pilot_qwen2_5_0_5b_hotpotqa_100",
        "#0072B2",
        "o",
    ),
    (
        "Qwen 1.5B",
        ROOT / "results" / "replication_qwen2_5_1_5b_hotpotqa_100",
        "#E69F00",
        "s",
    ),
    (
        "SmolLM2 1.7B",
        ROOT / "results" / "replication_smollm2_1_7b_hotpotqa_100",
        "#009E73",
        "^",
    ),
]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def percent_axis(axis, upper: float = 50) -> None:
    axis.set_ylim(0, upper)
    axis.set_ylabel("Percent of questions")
    axis.grid(axis="y", color="#d9d9d9", linewidth=0.6, alpha=0.8)
    axis.set_axisbelow(True)


def label_bars(axis, bars, decimals: int = 1, suffix: str = "") -> None:
    for bar in bars:
        height = bar.get_height()
        axis.annotate(
            f"{height:.{decimals}f}{suffix}",
            (bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.2,
        )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summaries = []
    gates = []
    for label, directory, color, marker in CONDITIONS:
        summaries.append((label, load_json(directory / "summary.json"), color, marker))
        gates.append((label, load_json(directory / "gate_summary.json"), color))

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(7.15, 5.6), constrained_layout=True)

    # (a) Accuracy over nested retrieval depth.
    ax = axes[0, 0]
    for label, summary, color, marker in summaries:
        depths = [row["k"] for row in summary["accuracy"]]
        accuracy = [100 * row["accuracy"] for row in summary["accuracy"]]
        ax.plot(
            depths,
            accuracy,
            color=color,
            marker=marker,
            markersize=5,
            linewidth=1.8,
            label=label,
        )
    ax.set_xticks([1, 2, 3, 5, 10])
    ax.set_xlabel("Nested retrieval depth, k")
    ax.set_ylabel("Answer accuracy (%)")
    ax.set_ylim(10, 45)
    ax.grid(color="#d9d9d9", linewidth=0.6, alpha=0.8)
    ax.set_title("(a) More evidence is not monotonic")
    ax.legend(frameon=False, ncol=1, loc="best")

    # (b) At-least-one and persistent reversal incidence.
    ax = axes[0, 1]
    x = np.arange(len(summaries))
    width = 0.34
    ear_at_k = [100 * summary["ear_at_k"] for _, summary, _, _ in summaries]
    p_ear = [100 * summary["p_ear"] for _, summary, _, _ in summaries]
    bars_a = ax.bar(x - width / 2, ear_at_k, width, color="#CC79A7", label="EAR@K")
    bars_b = ax.bar(x + width / 2, p_ear, width, color="#56B4E9", label="Persistent EAR")
    ax.set_xticks(x, ["Qwen\n0.5B", "Qwen\n1.5B", "SmolLM2\n1.7B"])
    percent_axis(ax, 38)
    ax.set_title("(b) Reversal incidence")
    ax.legend(frameon=False, loc="upper left")
    label_bars(ax, bars_a)
    label_bars(ax, bars_b)

    # (c) The gate suppresses answered harm, mostly by being conservative.
    ax = axes[1, 0]
    raw_ear = [100 * gate["overall"]["raw_ear"] for _, gate, _ in gates]
    gated_harm = [100 * gate["overall"]["gated_harmful"] for _, gate, _ in gates]
    bars_a = ax.bar(x - width / 2, raw_ear, width, color="#D55E00", label="Raw adjacent EAR")
    bars_b = ax.bar(x + width / 2, gated_harm, width, color="#0072B2", label="Gated answered harm")
    ax.set_xticks(x, ["Qwen\n0.5B", "Qwen\n1.5B", "SmolLM2\n1.7B"])
    percent_axis(ax, 11)
    ax.set_title("(c) Harm after lexical gating")
    ax.legend(frameon=False, loc="upper left")
    label_bars(ax, bars_a, decimals=2)
    label_bars(ax, bars_b, decimals=2)

    # (d) Population accuracy and coverage expose the cost of that reduction.
    ax = axes[1, 1]
    width = 0.24
    raw_accuracy = [100 * gate["final"]["raw_accuracy"] for _, gate, _ in gates]
    answered_accuracy = [100 * gate["final"]["answered_accuracy"] for _, gate, _ in gates]
    coverage = [100 * gate["final"]["coverage"] for _, gate, _ in gates]
    bars_a = ax.bar(x - width, raw_accuracy, width, color="#009E73", label="Raw accuracy")
    bars_b = ax.bar(x, answered_accuracy, width, color="#E69F00", label="Gated population accuracy")
    bars_c = ax.bar(x + width, coverage, width, color="#999999", label="Coverage")
    ax.set_xticks(x, ["Qwen\n0.5B", "Qwen\n1.5B", "SmolLM2\n1.7B"])
    percent_axis(ax, 82)
    ax.set_title("(d) Answer suppression is not free")
    ax.legend(frameon=False, loc="upper left", fontsize=7.2)
    label_bars(ax, bars_a)
    label_bars(ax, bars_b)
    label_bars(ax, bars_c)

    fig.savefig(OUT / "main_results.png", dpi=300, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()

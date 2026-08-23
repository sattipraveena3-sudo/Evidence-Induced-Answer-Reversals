# Evidence-Induced Answer Reversals in Retrieval-Augmented Generation

A reproducible research implementation for measuring **Evidence-Induced Answer Reversals (EAR)**: cases where a RAG system answers correctly with a smaller retrieved context and becomes incorrect after more evidence is added.

## Core metrics

- **EAR** — correct → incorrect transition rate
- **BCR** — incorrect → correct transition rate
- **RTB** — Retrieval Transition Balance = BCR − EAR
- **EAR@K** — fraction of questions with at least one reversal by maximum depth
- **P-EAR** — persistent reversals that never recover
- **FRD** — First Reversal Depth

The key identity is:

`Accuracy(k_b) - Accuracy(k_a) = BCR(k_a,k_b) - EAR(k_a,k_b)`

This is why aggregate Top-k accuracy can hide substantial harmful reversals.

## Project layout

```text
src/ear/
  schema.py       Data validation and normalization
  scoring.py      Exact-match and token-F1 scoring
  backends.py     Mock and OpenAI-compatible model backends
  runner.py       Generate Top-k answer trajectories
  analysis.py     Compute EAR/BCR/RTB/P-EAR/FRD + bootstrap CIs
  prepare.py      Dataset conversion utilities
scripts/
  run_smoke_test.sh
  run_openai_example.sh
configs/
  experiment.json
data/
  sample.jsonl
tests/
paper/
results/
```

## 1. Smoke test — no API key required

```bash
python -m pip install -e .
ear-run \
  --input data/sample.jsonl \
  --output results/mock_trajectories.jsonl \
  --backend mock \
  --depths 1,2,3,5

ear-analyze \
  --input results/mock_trajectories.jsonl \
  --outdir results/mock
```

The mock backend is **only for testing the pipeline**. Its numbers must never be used as research findings.

## 2. Real experiment with an OpenAI-compatible endpoint

Set credentials locally:

```bash
export OPENAI_API_KEY="YOUR_KEY"
```

Run:

```bash
ear-run \
  --input data/your_dataset.jsonl \
  --output results/trajectories.jsonl \
  --backend openai \
  --model gpt-4.1-mini \
  --depths 1,2,3,5,10 \
  --limit 500
```

Then:

```bash
ear-analyze \
  --input results/trajectories.jsonl \
  --outdir results/primary
```

## Input format

Each JSONL line:

```json
{
  "id": "q1",
  "question": "Who wrote The Trial?",
  "answers": ["Franz Kafka", "Kafka"],
  "passages": [
    "Rank-1 passage",
    "Rank-2 passage",
    "Rank-3 passage"
  ]
}
```

**Important:** `passages` must be one fixed retrieval ranking. Top-5 must be the exact Top-3 prefix plus two additional passages.

## Publication protocol

Recommended primary run:

- 500–1000 questions per dataset
- retrieval depths: 1, 2, 3, 5, 10
- deterministic generation (`temperature=0`)
- at least two QA datasets
- ideally two model families and two retrievers
- bootstrap 95% confidence intervals
- retain all C→W examples for qualitative analysis
- never report mock or synthetic numbers as empirical findings

## Generated outputs

`summary.json` — machine-readable metrics  
`summary.csv` — table-ready results  
`transitions.csv` — EAR/BCR/RTB per depth transition  
`reversal_examples.jsonl` — all observed C→W examples  
`trajectory_counts.csv` — trajectory taxonomy counts  

If matplotlib is installed, `ear-analyze --plots` also writes publication-ready PNG figures.

## Result requirement

This repository is considered complete only when a real primary experiment has been run. Publishable claims must come from `ear-analyze` outputs generated from real model trajectories, not the mock backend.

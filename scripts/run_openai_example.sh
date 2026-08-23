#!/usr/bin/env bash
set -euo pipefail
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY first}"
python -m pip install -e .
ear-run \
  --input data/primary.jsonl \
  --output results/primary_trajectories.jsonl \
  --backend openai \
  --model "${MODEL:-gpt-4.1-mini}" \
  --depths 1,2,3,5,10 \
  --limit "${LIMIT:-500}"
ear-analyze --input results/primary_trajectories.jsonl --outdir results/primary --plots

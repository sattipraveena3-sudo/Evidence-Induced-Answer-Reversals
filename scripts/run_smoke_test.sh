#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e .
ear-run --input data/sample.jsonl --output results/mock_trajectories.jsonl --backend mock --depths 1,2,3,5
ear-analyze --input results/mock_trajectories.jsonl --outdir results/mock

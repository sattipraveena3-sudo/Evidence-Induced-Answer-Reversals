#!/usr/bin/env bash
set -euo pipefail

pilot_model_dir="${EAR_MODEL_DIR:-/tmp/ear-models}"
pilot_model_path="${pilot_model_dir}/qwen2.5-0.5b-instruct-q4_k_m.gguf"
pilot_model_url="https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/9217f5db79a29953eb74d5343926648285ec7e67/qwen2.5-0.5b-instruct-q4_k_m.gguf?download=true"
pilot_model_sha="74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db"
pilot_input="${EAR_PILOT_INPUT:-/tmp/ear-hotpotqa-100.jsonl}"
pilot_results="${EAR_RESULTS_DIR:-results/pilot_qwen2_5_0_5b_hotpotqa_100}"
pilot_threads="${EAR_THREADS:-9}"

mkdir -p "${pilot_model_dir}" "${pilot_results}"
if [[ ! -f "${pilot_model_path}" ]]; then
  curl --location --fail --retry 3 \
    --output "${pilot_model_path}" "${pilot_model_url}"
fi
printf '%s  %s\n' "${pilot_model_sha}" "${pilot_model_path}" | sha256sum --check --status

python scripts/prepare_hotpotqa.py --output "${pilot_input}" --limit 100 --seed 7
ear-run \
  --input "${pilot_input}" \
  --output "${pilot_results}/trajectories.jsonl" \
  --backend llama-cpp \
  --model "${pilot_model_path}" \
  --depths 1,2,3,5,10 \
  --limit 100 \
  --temperature 0 \
  --context-size 4096 \
  --threads "${pilot_threads}" \
  --batch-size 512 \
  --seed 7 \
  --max-tokens 32 \
  --scoring contains \
  --gate lexical
ear-analyze \
  --input "${pilot_results}/trajectories.jsonl" \
  --outdir "${pilot_results}"

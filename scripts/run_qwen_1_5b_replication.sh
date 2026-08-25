#!/usr/bin/env bash
set -euo pipefail

replication_model_dir="${EAR_MODEL_DIR:-/tmp/ear-models}"
replication_model_path="${replication_model_dir}/qwen2.5-1.5b-instruct-q4_k_m.gguf"
replication_model_url="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/91cad51170dc346986eccefdc2dd33a9da36ead9/qwen2.5-1.5b-instruct-q4_k_m.gguf?download=true"
replication_model_sha="6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e"
replication_input="${EAR_REPLICATION_INPUT:-/tmp/ear-hotpotqa-100.jsonl}"
replication_results="${EAR_RESULTS_DIR:-results/replication_qwen2_5_1_5b_hotpotqa_100}"
replication_threads="${EAR_THREADS:-9}"
expected_input_sha="915d6b5706981b0f76e13bd56e3b81f8e09d11be09fd44ad1aa405aadb99f424"

mkdir -p "${replication_model_dir}" "${replication_results}"
if [[ ! -f "${replication_model_path}" ]]; then
  curl --location --fail --retry 3 \
    --output "${replication_model_path}" "${replication_model_url}"
fi
printf '%s  %s\n' "${replication_model_sha}" "${replication_model_path}" | sha256sum --check --status

python scripts/prepare_hotpotqa.py --output "${replication_input}" --limit 100 --seed 7
printf '%s  %s\n' "${expected_input_sha}" "${replication_input}" | sha256sum --check --status

ear-run \
  --input "${replication_input}" \
  --output "${replication_results}/trajectories.jsonl" \
  --backend llama-cpp \
  --model "${replication_model_path}" \
  --depths 1,2,3,5,10 \
  --limit 100 \
  --temperature 0 \
  --context-size 4096 \
  --threads "${replication_threads}" \
  --batch-size 512 \
  --seed 7 \
  --max-tokens 32 \
  --scoring contains \
  --gate lexical
ear-analyze \
  --input "${replication_results}/trajectories.jsonl" \
  --outdir "${replication_results}"

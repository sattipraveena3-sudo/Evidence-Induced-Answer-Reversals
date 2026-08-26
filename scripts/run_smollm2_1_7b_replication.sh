#!/usr/bin/env bash
set -euo pipefail

replication_model_dir="${EAR_MODEL_DIR:-/tmp/ear-models}"
replication_model_path="${replication_model_dir}/smollm2-1.7b-instruct-q4_k_m.gguf"
replication_model_url="https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF/resolve/6a7e79393ef2957e087f11fce1e50476799e313c/smollm2-1.7b-instruct-q4_k_m.gguf?download=true"
replication_model_sha="decd2598bc2c8ed08c19adc3c8fdd461ee19ed5708679d1c54ef54a5a30d4f33"
replication_input="${EAR_REPLICATION_INPUT:-/tmp/ear-hotpotqa-100.jsonl}"
replication_results="${EAR_RESULTS_DIR:-results/replication_smollm2_1_7b_hotpotqa_100}"
qwen_1_5b_trajectories="${EAR_PRIMARY_BASELINE_TRAJECTORIES:-results/replication_qwen2_5_1_5b_hotpotqa_100/trajectories.jsonl}"
qwen_0_5b_trajectories="${EAR_SECONDARY_BASELINE_TRAJECTORIES:-results/pilot_qwen2_5_0_5b_hotpotqa_100/trajectories.jsonl}"
primary_comparison="${EAR_PRIMARY_COMPARISON_DIR:-results/comparison_qwen2_5_1_5b_vs_smollm2_1_7b_hotpotqa_100}"
secondary_comparison="${EAR_SECONDARY_COMPARISON_DIR:-results/comparison_qwen2_5_0_5b_vs_smollm2_1_7b_hotpotqa_100}"
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
  --outdir "${replication_results}" \
  --plots

ear-compare \
  --baseline "${qwen_1_5b_trajectories}" \
  --candidate "${replication_results}/trajectories.jsonl" \
  --outdir "${primary_comparison}" \
  --baseline-label "Qwen2.5-1.5B-Instruct-Q4_K_M" \
  --candidate-label "SmolLM2-1.7B-Instruct-Q4_K_M" \
  --plots

ear-compare \
  --baseline "${qwen_0_5b_trajectories}" \
  --candidate "${replication_results}/trajectories.jsonl" \
  --outdir "${secondary_comparison}" \
  --baseline-label "Qwen2.5-0.5B-Instruct-Q4_K_M" \
  --candidate-label "SmolLM2-1.7B-Instruct-Q4_K_M" \
  --plots

qwen_1_5b_exact="/tmp/ear-qwen2.5-1.5b-hotpotqa-100-exact.jsonl"
qwen_0_5b_exact="/tmp/ear-qwen2.5-0.5b-hotpotqa-100-exact.jsonl"
replication_exact="/tmp/ear-smollm2-1.7b-hotpotqa-100-exact.jsonl"
ear-rescore --input "${qwen_1_5b_trajectories}" --output "${qwen_1_5b_exact}" --scoring exact
ear-rescore --input "${qwen_0_5b_trajectories}" --output "${qwen_0_5b_exact}" --scoring exact
ear-rescore \
  --input "${replication_results}/trajectories.jsonl" \
  --output "${replication_exact}" \
  --scoring exact
ear-analyze \
  --input "${replication_exact}" \
  --outdir "${replication_results}/exact_match_sensitivity"
ear-compare \
  --baseline "${qwen_1_5b_exact}" \
  --candidate "${replication_exact}" \
  --outdir "${primary_comparison}/exact_match_sensitivity" \
  --baseline-label "Qwen2.5-1.5B-Instruct-Q4_K_M" \
  --candidate-label "SmolLM2-1.7B-Instruct-Q4_K_M"
ear-compare \
  --baseline "${qwen_0_5b_exact}" \
  --candidate "${replication_exact}" \
  --outdir "${secondary_comparison}/exact_match_sensitivity" \
  --baseline-label "Qwen2.5-0.5B-Instruct-Q4_K_M" \
  --candidate-label "SmolLM2-1.7B-Instruct-Q4_K_M"

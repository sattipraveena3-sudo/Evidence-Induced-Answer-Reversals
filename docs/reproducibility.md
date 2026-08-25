# Reproducibility

Pilot seed: 7. Generation temperature: 0. Retrieval ranking: deterministic lexical overlap over the ten HotpotQA distractor contexts. Evaluated retrieval depths: 1, 2, 3, 5, 10. The same ranked prefix is reused at every depth.

The lexical gate defaults are support threshold 0.8 and comparative margin 0.2. The model verifier uses the fixed JSON contract in `GATE_PROTOCOL.md`. Both compare candidates using only the current Top-k prefix; neither receives gold answers or future evidence.

## Published free pilot

- Dataset: HotpotQA distractor development set, 100 rows sampled after a Python `random.Random(7)` shuffle
- Prepared-sample SHA-256: `915d6b5706981b0f76e13bd56e3b81f8e09d11be09fd44ad1aa405aadb99f424`
- Generator: `Qwen/Qwen2.5-0.5B-Instruct-GGUF`, file `qwen2.5-0.5b-instruct-q4_k_m.gguf`
- Model SHA-256: `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`
- Runtime: `llama-cpp-python==0.3.35`, context 4096, batch 512, 9 CPU threads, seed 7, maximum 32 new tokens
- Scoring: normalized contiguous whole-token containment for binary trajectory labels plus normalized token F1
- Uncertainty: 3,000 question-level bootstrap resamples with seed 7

Run `python -m pip install -e '.[local]'` followed by `scripts/run_free_pilot.sh`. The exact completed-run metadata and artifact digests are frozen in the [manifest](../results/pilot_qwen2_5_0_5b_hotpotqa_100/manifest.json).

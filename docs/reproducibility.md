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

## Published 1.5B scale replication

- Pre-generation local Git objects: preregistration `38c40aa6c9e4f030f73524a3b5c96732119c369e`; paired analysis `ee13853f4d0d652fbf19badd77346ef67063eb80`. Their content-equivalent public commits are `be12be3b8499a95ce6a1c4a64c614396fff4a267` and `74484164ee4a0c5949bf32ff5dafcb19ef97423b`. The connected transport published them after the run, so this was prospectively frozen but not independently publicly timestamped before generation.
- Dataset, order, ranking, prompts, depths, decoding, scoring, gate, and bootstrap settings are identical to the 0.5B pilot.
- Generator: `Qwen/Qwen2.5-1.5B-Instruct-GGUF` revision `91cad51170dc346986eccefdc2dd33a9da36ead9`, file `qwen2.5-1.5b-instruct-q4_k_m.gguf`.
- Model SHA-256: `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`.
- Runtime: `llama-cpp-python==0.3.35`, context 4096, batch 512, 9 CPU threads, seed 7, maximum 32 new tokens.
- Raw-trajectory SHA-256: `6ddbaaa180291cf4b767e167e02879cf8736019a53f75924e944bbd488a91086`.

Run `python -m pip install -e '.[local,plots]'` followed by `scripts/run_qwen_1_5b_replication.sh`. Exact metadata, execution notes, audit counts, and artifact hashes are in the [replication manifest](../results/replication_qwen2_5_1_5b_hotpotqa_100/manifest.json).

## Published SmolLM2 1.7B independent-family replication

- Independently public pre-generation commit: `f757d862e59f5fd25b70a5463f0ec639e0c07888`; tree `90744d2f52cecaf693d8ee455fd4f2ba2e67db5d`.
- Dataset, order, ranking, prompts, depths, decoding, scoring, gate, and bootstrap settings are identical to both Qwen conditions.
- Generator: `HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF` pinned file revision `6a7e79393ef2957e087f11fce1e50476799e313c`, file `smollm2-1.7b-instruct-q4_k_m.gguf`.
- Model SHA-256: `decd2598bc2c8ed08c19adc3c8fdd461ee19ed5708679d1c54ef54a5a30d4f33`.
- Runtime: `llama-cpp-python==0.3.35`, context 4096, batch 512, 9 CPU threads, seed 7, maximum 32 new tokens.
- Raw-trajectory SHA-256: `8b4712f32c7ea0add400bc1eb3e72165741816a4e680e47ec6690fc0a46f09b5`.

Run `python -m pip install -e '.[local,plots]'` followed by `scripts/run_smollm2_1_7b_replication.sh`. Exact metadata, execution notes, audit counts, comparison hashes, and limitations are in the [replication manifest](../results/replication_smollm2_1_7b_hotpotqa_100/manifest.json).

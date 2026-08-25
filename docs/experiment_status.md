# Experiment status

## Verified software milestones

- Raw Top-k trajectory generation
- EAR/BCR/RTB/P-EAR/FRD analysis with bootstrap confidence intervals
- Change-triggered stateful gate with accept, retain, and abstain actions
- Gold-label-free deterministic lexical verifier baseline
- Fixed-JSON model-verifier interface for OpenAI-compatible local or hosted endpoints
- Gate analysis that reports harmful answered transitions separately from abstentions
- Twelve passing unit tests and a deterministic end-to-end gate smoke run
- Local GGUF backend with model hashing, token usage, and per-generation latency
- Whole-token containment scoring with a regression test preventing `no` from matching `unknown`

## Completed exploratory pilot

On 2026-08-25, the repository completed a zero-cost, 100-question HotpotQA distractor-dev pilot with Qwen2.5-0.5B-Instruct Q4_K_M, deterministic lexical-overlap ranking, Top-k depths 1/2/3/5/10, temperature 0, and the lexical evidence-stability gate.

The pilot observed EAR@K = 23% (bootstrap 95% CI 15%–32%) and P-EAR = 12% (6%–19%). Across 400 adjacent-depth opportunities, raw EAR was 6.25% and BCR was 8.5%. The lexical gate reduced answered harmful transitions to 0.25%, but final coverage fell to 55% and it retained only 41.2% of raw beneficial repairs. These trade-offs make it a diagnostic baseline, not a validated mitigation.

The raw trajectories, result tables, hashes, and limitations are in the [pilot result card](../results/pilot_qwen2_5_0_5b_hotpotqa_100/RESULTS.md).

## Next empirical milestone

Run the pre-registered primary matrix with at least two open-weight model families and two retrievers on 500–1000 questions per condition. The single small-model pilot is not a confirmatory result and cannot support broad RAG reliability claims.

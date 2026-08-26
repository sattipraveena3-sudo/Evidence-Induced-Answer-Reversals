# Experiment status

## Verified software milestones

- Raw Top-k trajectory generation
- EAR/BCR/RTB/P-EAR/FRD analysis with bootstrap confidence intervals
- Change-triggered stateful gate with accept, retain, and abstain actions
- Gold-label-free deterministic lexical verifier baseline
- Fixed-JSON model-verifier interface for OpenAI-compatible local or hosted endpoints
- Gate analysis that reports harmful answered transitions separately from abstentions
- Fifteen passing unit tests and a deterministic end-to-end gate smoke run
- Local GGUF backend with model hashing, token usage, and per-generation latency
- Whole-token containment scoring with a regression test preventing `no` from matching `unknown`

## Completed exploratory pilot

On 2026-08-25, the repository completed a zero-cost, 100-question HotpotQA distractor-dev pilot with Qwen2.5-0.5B-Instruct Q4_K_M, deterministic lexical-overlap ranking, Top-k depths 1/2/3/5/10, temperature 0, and the lexical evidence-stability gate.

The pilot observed EAR@K = 23% (bootstrap 95% CI 15%–32%) and P-EAR = 12% (6%–19%). Across 400 adjacent-depth opportunities, raw EAR was 6.25% and BCR was 8.5%. The lexical gate reduced answered harmful transitions to 0.25%, but final coverage fell to 55% and it retained only 41.2% of raw beneficial repairs. These trade-offs make it a diagnostic baseline, not a validated mitigation.

The raw trajectories, result tables, hashes, and limitations are in the [pilot result card](../results/pilot_qwen2_5_0_5b_hotpotqa_100/RESULTS.md).

## Completed scale replication

On 2026-08-25, the prospectively frozen Qwen2.5-1.5B condition completed all 500 generations on the exact ordered pilot sample. EAR@K was 22% (95% CI 14%–30%) and persistent EAR was 13% (7%–20%). Versus 0.5B, paired differences were −1 point for EAR@K (−11 to +10) and +1 point for persistent EAR (−8 to +10). Only 8 reversal questions were shared across sizes (Jaccard 0.216). The manifest records that public GitHub transport occurred after the run rather than claiming an independently public pre-run timestamp.

The [1.5B result card](../results/replication_qwen2_5_1_5b_hotpotqa_100/RESULTS.md), [paired comparison](../results/comparison_qwen2_5_0_5b_vs_1_5b_hotpotqa_100/RESULTS.md), raw trajectories, exact-match sensitivity, plots, audit, and hashes are committed artifacts.

## Completed independent-family replication

On 2026-08-26, SmolLM2 1.7B completed all 500 generations after the frozen condition was publicly timestamped in GitHub commit `f757d862…`. It used the exact ordered 100-question sample, ranking, nested depths, prompt, decoding, scoring, and gate from both Qwen2.5 conditions.

EAR@K was 32% (95% CI 23%–41%), persistent EAR was 21% (13%–30%), and exact-match EAR@K was 25% (17%–34%). Versus size-near Qwen1.5B, the overall EAR@K difference was +10 points (−1 to +21), while the prespecified k=5→10 transition showed a clearer +11-point EAR difference (+5 to +18). Only 11 reversal questions were shared (Jaccard 0.256).

The [result card](../results/replication_smollm2_1_7b_hotpotqa_100/RESULTS.md), [primary paired comparison](../results/comparison_qwen2_5_1_5b_vs_smollm2_1_7b_hotpotqa_100/RESULTS.md), [scoring audit](../results/replication_smollm2_1_7b_hotpotqa_100/SCORING_AUDIT.md), raw trajectories, plots, and manifest are committed artifacts.

## Next milestone after SmolLM2

Preregister and run a second retriever while holding the sample and one model fixed, then scale to the 500–1000-question primary matrix. The current diagnostic conditions do not support broad prevalence or mitigation claims.

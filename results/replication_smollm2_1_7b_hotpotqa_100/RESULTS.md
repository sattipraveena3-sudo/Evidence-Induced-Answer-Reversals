# SmolLM2 1.7B independent-family replication result card

## Status and scope

Completed on 2026-08-26: 100 matched HotpotQA distractor-development questions, five nested retrieval depths, and 500 genuine CPU generations. The frozen protocol was publicly timestamped on GitHub `main` in commit `f757d862e59f5fd25b70a5463f0ec639e0c07888` before any SmolLM2 answer was generated.

This is a preregistered **independent model-family diagnostic replication**. It tests whether the EAR signal survives a move from Qwen2.5 to SmolLM2; it is not a controlled causal estimate of architecture or training effects and is not yet the larger multi-retriever primary experiment.

The primary hypothesis was supported: SmolLM2 produced harmful correct-to-incorrect transitions as evidence depth increased.

## Frozen condition

| Component | Value |
|---|---|
| Generator | Official SmolLM2-1.7B-Instruct, Q4_K_M GGUF |
| Model integrity | Revision `6a7e793…`; SHA-256 `decd2598…` |
| Runtime | llama-cpp-python 0.3.35, CPU only |
| Decoding | temperature 0, seed 7, maximum 32 new tokens |
| Dataset | Exact ordered seed-7 100-question sample used by both Qwen conditions |
| Ranking | Deterministic lexical overlap over 10 provided contexts |
| Depths | 1, 2, 3, 5, 10 |
| Binary scoring | Normalized contiguous whole-token answer containment |
| Sensitivity | Normalized exact match |
| Gate | Lexical support threshold 0.8, margin 0.2 |

The preregistration is in [`docs/SMOLLM2_1_7B_FAMILY_REPLICATION.md`](../../docs/SMOLLM2_1_7B_FAMILY_REPLICATION.md); exact provenance and hashes are in [`manifest.json`](manifest.json).

## Raw trajectory results

| Depth | Answer-span accuracy | Bootstrap 95% CI | Mean token F1 |
|---:|---:|---:|---:|
| 1 | 25% | 17%–34% | 0.262 |
| 2 | 30% | 21%–40% | 0.328 |
| 3 | 24% | 16%–33% | 0.269 |
| 5 | 24% | 16%–32% | 0.257 |
| 10 | 18% | 11%–25% | 0.201 |

| Transition | EAR | BCR | RTB = BCR − EAR |
|---|---:|---:|---:|
| 1 → 2 | 5% | 10% | +5 pp |
| 2 → 3 | 9% | 3% | −6 pp |
| 3 → 5 | 7% | 7% | 0 pp |
| 5 → 10 | 15% | 9% | −6 pp |

- EAR@K: **32%** (bootstrap 95% CI 23%–41%).
- Persistent EAR: **21%** (13%–30%).
- Median first reversal depth: **5**.
- Across 400 adjacent-depth opportunities: raw EAR **9%**, raw BCR **7.25%**.
- Trajectory counts: 57 persistent failures, 7 stable correct, 4 beneficial recoveries, 17 temporary reversals, 9 harmful reversals, and 6 oscillations.

Accuracy peaks at k=2 and then falls by 12 points by k=10. The largest harmful transition is k=5→10, where 15 questions become incorrect and only 9 recover.

## Primary paired comparison with Qwen2.5 1.5B

| Metric | Qwen1.5B | SmolLM2 | SmolLM2 − Qwen | Paired 95% CI |
|---|---:|---:|---:|---:|
| Accuracy@1 | 22% | 25% | +3 pp | −5 to +11 pp |
| Accuracy@2 | 36% | 30% | −6 pp | −14 to +2 pp |
| Accuracy@3 | 37% | 24% | −13 pp | −22 to −5 pp |
| Accuracy@5 | 32% | 24% | −8 pp | −17 to +1 pp |
| Accuracy@10 | 40% | 18% | −22 pp | −33 to −11 pp |
| EAR@K | 22% | 32% | +10 pp | −1 to +21 pp |
| Persistent EAR | 13% | 21% | +8 pp | −2 to +18 pp |
| Overall adjacent EAR | 5.75% | 9% | +3.25 pp | 0 to +6.25 pp |
| Overall adjacent BCR | 10.25% | 7.25% | −3 pp | −6.25 to +0.25 pp |

The overall EAR@K and persistent-EAR intervals remain too wide to establish a general family-rate difference. The deep transition is sharper: at k=5→10, SmolLM2 EAR exceeds Qwen1.5B by **11 points** (paired 95% CI +5 to +18). Full estimates are in the [primary comparison result card](../comparison_qwen2_5_1_5b_vs_smollm2_1_7b_hotpotqa_100/RESULTS.md).

Reversal identity again changes substantially: 11 questions reverse under both models, 11 only under Qwen1.5B, and 21 only under SmolLM2 (Jaccard 0.256).

## Exact-match sensitivity

Exact-match accuracy is 21%, 27%, 21%, 20%, and 14% across depths. EAR@K remains **25%** (95% CI 17%–34%), persistent EAR remains **18%** (11%–26%), and median first reversal depth remains 5.

Versus Qwen1.5B under exact match, the paired EAR@K difference is +8 points (−2 to +18), persistent-EAR difference is +7 points (−2 to +16), and k=5→10 EAR difference is +7 points (+2 to +13). Thus the qualitative deep-context result survives a stricter binary rule.

## Lexical gate trade-off

The gate lowers answered harmful transitions from 9% to 0.25% across adjacent opportunities, a 97.2% relative reduction. It is still a negative diagnostic baseline, not a validated mitigation:

- Final coverage: **52%**.
- Final answered accuracy over all questions: **17%**; selective accuracy among answered questions: **32.7%**.
- Raw final accuracy: **18%**.
- BCR retention: **41.4%** (12 of 29 raw beneficial repairs retained).
- Decisions: 100 initial, 165 unchanged, 22 accept-new, 66 retain-previous, and 147 abstain.

Most apparent harm reduction comes with abstention, lost correct answers, and suppressed repairs.

## Audit and limitations

Every saved label was recomputed with no mismatch. Manual review found 10 valid expanded containment-only outputs, 3 clear false-positive outputs, and 1 mixed output. Of 32 primary reversal questions, 30 have an unambiguous correct pre-reversal answer and 27 have a clearly incorrect later answer. Six trajectories require explicit semantic caution. See [`SCORING_AUDIT.md`](SCORING_AUDIT.md).

The sample is small, absolute QA accuracy is low, both models are quantized, and retrieval uses one lexical ranking. The audit has one non-blinded reviewer. This condition establishes cross-family reproducibility and identifies a deep-evidence failure concentration; it does not establish population prevalence, causality, or mitigation effectiveness.

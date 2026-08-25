# Qwen2.5-1.5B scale-replication result card

## Status and scope

Completed on 2026-08-25 after the condition and paired analysis were committed locally: 100 matched HotpotQA distractor-development questions, five retrieval depths, and 500 genuine CPU generations. This is a prospectively frozen **within-family scale replication** of the 0.5B pilot. It is not an independent model-family replication or a confirmatory primary experiment. The connected GitHub transport recreated content-equivalent public commits after the run, so the manifest distinguishes the original local pre-generation hashes from their public equivalents; this was not independently publicly timestamped before generation.

The primary hypothesis was supported: the 1.5B condition produced harmful correct-to-incorrect transitions. The effect was not rare in this sample, but uncertainty remains wide and the result must not be generalized beyond this condition.

## Frozen condition

| Component | Value |
|---|---|
| Generator | Official Qwen2.5-1.5B-Instruct, Q4_K_M GGUF |
| Model integrity | Revision `91cad511…`; SHA-256 `6a1a2eb…` |
| Runtime | llama-cpp-python 0.3.35, CPU only |
| Decoding | temperature 0, seed 7, maximum 32 new tokens |
| Dataset | Exact ordered seed-7 100-question sample from the 0.5B pilot |
| Ranking | Deterministic lexical overlap over 10 provided contexts |
| Depths | 1, 2, 3, 5, 10 |
| Binary scoring | Normalized contiguous whole-token answer containment |
| Sensitivity | Normalized exact match |
| Gate | Lexical support threshold 0.8, margin 0.2 |

The preregistration is in [`docs/QWEN_1_5B_REPLICATION.md`](../../docs/QWEN_1_5B_REPLICATION.md); exact run provenance and hashes are in [`manifest.json`](manifest.json).

## Raw trajectory results

| Depth | Answer-span accuracy | Bootstrap 95% CI | Mean token F1 |
|---:|---:|---:|---:|
| 1 | 22% | 14%–30% | 0.276 |
| 2 | 36% | 27%–45% | 0.362 |
| 3 | 37% | 28%–47% | 0.384 |
| 5 | 32% | 23%–41% | 0.340 |
| 10 | 40% | 30%–49% | 0.423 |

| Transition | EAR | BCR | RTB = BCR − EAR |
|---|---:|---:|---:|
| 1 → 2 | 4% | 18% | +14 pp |
| 2 → 3 | 5% | 6% | +1 pp |
| 3 → 5 | 10% | 5% | −5 pp |
| 5 → 10 | 4% | 12% | +8 pp |

- EAR@K: **22%** (bootstrap 95% CI 14%–30%); 22 questions had at least one primary reversal.
- Persistent EAR: **13%** (7%–20%).
- Median first reversal depth: **5**.
- Across 400 adjacent-depth opportunities: raw EAR 5.75%, raw BCR 10.25%.
- Trajectory counts: 46 persistent failures, 11 stable correct, 21 beneficial recoveries, 15 temporary reversals, 4 harmful reversals, and 3 oscillations.

The curve is non-monotonic: accuracy rises sharply by k=3, falls five points at k=5, and recovers by k=10. Aggregate final accuracy therefore conceals both harmful and beneficial movement.

## Paired comparison with 0.5B

| Metric | 0.5B | 1.5B | Paired difference | Paired bootstrap 95% CI |
|---|---:|---:|---:|---:|
| Accuracy@1 | 23% | 22% | −1 pp | −9 to +7 pp |
| Accuracy@2 | 22% | 36% | +14 pp | +5 to +23 pp |
| Accuracy@3 | 27% | 37% | +10 pp | 0 to +20 pp |
| Accuracy@5 | 27% | 32% | +5 pp | −5 to +15 pp |
| Accuracy@10 | 32% | 40% | +8 pp | −3 to +18 pp |
| EAR@K | 23% | 22% | −1 pp | −11 to +10 pp |
| Persistent EAR | 12% | 13% | +1 pp | −8 to +10 pp |
| Overall adjacent EAR | 6.25% | 5.75% | −0.5 pp | −3.25 to +2.5 pp |
| Overall adjacent BCR | 8.5% | 10.25% | +1.75 pp | −1 to +4.25 pp |

The 1.5B model is clearly better at k=2 under the primary metric, but this sample does **not** establish that greater model scale lowers harmful-reversal incidence: the EAR and persistent-EAR intervals span meaningful changes in both directions.

Reversal identity also changed substantially. Only 8 questions reversed under both sizes; 15 were unique to 0.5B and 14 unique to 1.5B, for Jaccard overlap 0.216. Similar aggregate rates therefore hide mostly different failure sets.

Full paired outputs are in the [comparison result card](../comparison_qwen2_5_0_5b_vs_1_5b_hotpotqa_100/RESULTS.md).

## Exact-match sensitivity

Exact-match accuracy was 19%, 26%, 29%, 25%, and 30% across the five depths. EAR@K remained 17% (95% CI 10%–24%), persistent EAR remained 11% (5%–17%), and median first reversal depth remained 5. The exact paired EAR@K difference versus 0.5B was −2 points (−12 to +8), again providing no evidence of a scale-driven reduction.

## Lexical gate trade-off

The gate reduced answered harmful transitions from 5.75% to 0.5% across all adjacent opportunities, a 91.3% relative reduction. That is not a mitigation success in isolation:

- Final coverage: 61%.
- Final answered accuracy over all questions: 22%; selective accuracy among answered questions: 36.1%.
- Raw final accuracy: 40%.
- BCR retention: 29.3% (12 of 41 raw beneficial repairs retained).
- Decisions: 100 initial, 185 unchanged, 24 accept-new, 42 retain-previous, and 149 abstain.

The same negative conclusion as the 0.5B pilot holds more strongly on repair retention: the lexical gate suppresses most useful corrections and loses many correct final answers.

## Scoring audit and limitations

Every saved primary label was recomputed with no mismatch. A complete manual review of all 17 distinct containment-only positive outputs found 15 valid expanded answers, one clear contradictory false positive, and one ambiguous indirect match. Of 22 primary reversal questions, 21 had an unambiguous correct pre-reversal answer; the remaining J35 trajectory is scoring-sensitive. See [`SCORING_AUDIT.md`](SCORING_AUDIT.md).

The sample is small, the QA accuracy is low, both generators are quantized members of one model family, and retrieval is one lexical ranking. The audit used one non-blinded reviewer. The result establishes a reproducible within-family signal and a sharper evaluation problem; it does not establish prevalence across RAG systems, causality, or a validated gate.

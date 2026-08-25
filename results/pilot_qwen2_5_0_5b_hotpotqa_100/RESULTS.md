# Zero-cost open-weight pilot result card

## Status and scope

Completed on 2026-08-25: 100 HotpotQA distractor-dev questions, five retrieval depths, and 500 genuine local-model generations. This is an exploratory feasibility pilot with one very small quantized model and one lexical ranking. It is not the pre-registered multi-model primary experiment and must not be generalized to other RAG systems.

## Frozen condition

| Component | Value |
|---|---|
| Generator | Qwen2.5-0.5B-Instruct, Q4_K_M GGUF |
| Runtime | llama-cpp-python 0.3.35, CPU only |
| Decoding | temperature 0, seed 7, maximum 32 new tokens |
| Dataset | HotpotQA distractor dev, deterministic seed-7 sample, n=100 |
| Ranking | deterministic lexical overlap over 10 provided contexts |
| Depths | 1, 2, 3, 5, 10 |
| Binary scoring | normalized contiguous whole-token answer containment |
| Additional scoring | normalized token F1 |
| Gate | lexical support threshold 0.8, margin 0.2 |

## Raw trajectory results

| Depth | Answer-span accuracy | Bootstrap 95% CI | Mean token F1 |
|---:|---:|---:|---:|
| 1 | 23% | 15%–31% | 0.251 |
| 2 | 22% | 14%–30% | 0.237 |
| 3 | 27% | 18%–36% | 0.260 |
| 5 | 27% | 19%–36% | 0.322 |
| 10 | 32% | 23%–41% | 0.328 |

| Transition | EAR | BCR | RTB = BCR − EAR |
|---|---:|---:|---:|
| 1 → 2 | 9% | 8% | −1 pp |
| 2 → 3 | 4% | 9% | +5 pp |
| 3 → 5 | 5% | 5% | 0 pp |
| 5 → 10 | 7% | 12% | +5 pp |

- EAR@K: 23% (bootstrap 95% CI 15%–32%); 23 questions had at least one correct-to-incorrect transition.
- Persistent EAR: 12% (6%–19%).
- Median first reversal depth: 3.
- Trajectory counts: 54 persistent failures, 10 stable correct, 13 beneficial recoveries, 17 temporary reversals, 3 oscillations, and 3 harmful reversals.

The aggregate k=1 to k=10 accuracy gain therefore hides substantial bidirectional movement. Every adjacent transition satisfies `Δaccuracy = BCR − EAR` exactly.

### Exact-match sensitivity

Rescoring the unchanged model answers with normalized exact match reduced absolute accuracy, as expected, but preserved the reversal signal: accuracy was 20%, 17%, 19%, 26%, and 29% across the five depths; EAR@K was 19% (95% CI 12%–27%); and persistent EAR was 10% (5%–16%). The qualitative conclusion that aggregate gains conceal harmful per-question reversals therefore does not depend on answer-span containment.

## Lexical gate trade-off

Across 400 adjacent-depth opportunities, raw EAR was 6.25% and raw BCR was 8.5%. The gate's answered harmful-transition rate was 0.25%, a 96% relative reduction, but this number is not a free reliability gain:

- Final coverage: 55%.
- Final answered accuracy over all questions: 22%; selective accuracy among answered questions: 40%.
- Raw final accuracy: 32%.
- BCR retention: 41.2% (14 of 34 raw beneficial repairs retained).
- Correct-to-abstain transitions: 3.75% of all opportunities.
- Decisions across 500 depth steps: 100 initial, 163 unchanged, 24 accept-new, 43 retain-previous, and 170 abstain.

The lexical verifier is consequently a negative/diagnostic baseline: it blocks most measured harm, but abstains too often and suppresses most useful repairs. The next verifier must improve this harm–repair–coverage frontier.

## Integrity and limitations

- Raw model answers, token usage, latency, gate decisions, and hashes are retained in `trajectories.jsonl`.
- A pre-publication audit corrected the old substring matcher to whole-token matching; this prevents `no` from matching `unknown`. The saved model-answer content was unchanged and has canonical SHA-256 `64dcde902b296b30521f2b82b57b01e8ebe3a60e000a55db867bc6b7ef6a330a`.
- All 23 reversal trajectories were manually inspected after rescoring.
- The 0.5B model has low absolute QA performance, the sample is small, the ranking is lexical, and only one model family was tested. Confidence intervals are correspondingly wide.
- No causal mechanism or general mitigation effectiveness is claimed from this pilot.

See `manifest.json` for exact provenance and artifact hashes. Reproduce with `python -m pip install -e '.[local]'` and `scripts/run_free_pilot.sh`.

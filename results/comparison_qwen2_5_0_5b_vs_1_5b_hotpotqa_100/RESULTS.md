# Paired Qwen2.5 0.5B versus 1.5B result card

## Design

This is a paired, within-family model-scale comparison on the exact same 100 ordered HotpotQA questions, fixed lexical rankings, prompts, depths, decoding settings, scoring, and gate. Only the official Qwen2.5 parameter scale and corresponding pinned GGUF file changed. Question-level paired bootstraps use 3,000 resamples with seed 7; adjacent-transition summaries resample whole question trajectories.

## Main finding

Scaling from 0.5B to 1.5B improved answer accuracy at some depths, especially k=2, but did not measurably reduce harmful-reversal incidence in this sample.

| Metric | 0.5B | 1.5B | 1.5B − 0.5B | Paired 95% CI |
|---|---:|---:|---:|---:|
| Accuracy@1 | 23% | 22% | −1 pp | −9 to +7 pp |
| Accuracy@2 | 22% | 36% | +14 pp | +5 to +23 pp |
| Accuracy@3 | 27% | 37% | +10 pp | 0 to +20 pp |
| Accuracy@5 | 27% | 32% | +5 pp | −5 to +15 pp |
| Accuracy@10 | 32% | 40% | +8 pp | −3 to +18 pp |
| EAR@K | 23% | 22% | −1 pp | −11 to +10 pp |
| Persistent EAR | 12% | 13% | +1 pp | −8 to +10 pp |
| Adjacent EAR | 6.25% | 5.75% | −0.5 pp | −3.25 to +2.5 pp |
| Adjacent BCR | 8.5% | 10.25% | +1.75 pp | −1 to +4.25 pp |

The reversal sets overlapped weakly:

- Shared: 8 questions.
- 0.5B only: 15.
- 1.5B only: 14.
- Neither: 63.
- Jaccard overlap: 0.216.

Thus, aggregate reversal rates were similar while most affected questions differed. This makes failure-set identity and trajectory-level analysis more informative than a single average stability number.

## Exact-match sensitivity

With exact match, EAR@K was 19% for 0.5B and 17% for 1.5B; the paired difference was −2 points (95% CI −12 to +8). Persistent EAR was 10% and 11%, respectively, a +1 point difference (−8 to +10). The conclusion remains unchanged.

## Interpretation boundary

This is a 100-question scale replication inside one model family, not evidence that model size generally has no effect. The intervals remain wide, and the low reversal-set overlap may reflect sampling variance, genuine scale-specific behavior, or both. A second model family, second retriever, and larger preregistered samples are still required.

Machine-readable estimates are in [`comparison.json`](comparison.json), membership is in [`reversal_set_membership.csv`](reversal_set_membership.csv), and the exact-match version is in [`exact_match_sensitivity/`](exact_match_sensitivity/).

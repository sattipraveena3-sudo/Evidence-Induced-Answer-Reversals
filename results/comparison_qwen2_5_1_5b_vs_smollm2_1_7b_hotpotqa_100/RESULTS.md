# Paired Qwen2.5 1.5B versus SmolLM2 1.7B result card

## Design

This preregistered cross-family comparison uses the exact same 100 ordered HotpotQA questions, fixed lexical rankings, nested evidence prefixes, prompt, decoding settings, scoring, and gate. Qwen2.5 1.5B is the prespecified primary comparator because its scale is close to SmolLM2 1.7B. Question-level paired bootstraps use 3,000 resamples with seed 7; adjacent-transition summaries resample whole question trajectories.

The SmolLM2 condition was publicly timestamped in GitHub commit `f757d862…` before generation. No result-dependent tuning occurred.

## Main finding

EAR generalizes to a second model family. SmolLM2 is less accurate at deeper evidence depths and has a concentrated excess of harmful reversals from k=5 to k=10. The sample does not precisely establish a general difference in EAR@K across families.

| Metric | Qwen1.5B | SmolLM2 | SmolLM2 − Qwen | Paired 95% CI |
|---|---:|---:|---:|---:|
| Accuracy@1 | 22% | 25% | +3 pp | −5 to +11 pp |
| Accuracy@2 | 36% | 30% | −6 pp | −14 to +2 pp |
| Accuracy@3 | 37% | 24% | −13 pp | −22 to −5 pp |
| Accuracy@5 | 32% | 24% | −8 pp | −17 to +1 pp |
| Accuracy@10 | 40% | 18% | −22 pp | −33 to −11 pp |
| EAR@K | 22% | 32% | +10 pp | −1 to +21 pp |
| Persistent EAR | 13% | 21% | +8 pp | −2 to +18 pp |
| Adjacent EAR | 5.75% | 9% | +3.25 pp | 0 to +6.25 pp |
| Adjacent BCR | 10.25% | 7.25% | −3 pp | −6.25 to +0.25 pp |

At k=5→10, EAR is 4% for Qwen1.5B and 15% for SmolLM2, a paired difference of **+11 points** (+5 to +18). SmolLM2 accuracy simultaneously falls from 24% to 18%, while Qwen rises from 32% to 40%. This local transition—not the imprecise overall family-rate difference—is the clearest comparative finding.

## Failure-set identity

- Shared reversal questions: 11.
- Qwen1.5B only: 11.
- SmolLM2 only: 21.
- Neither: 57.
- Jaccard overlap: 0.256.

The low overlap means the same aggregate metric covers largely model-specific failures. A robust verifier must therefore generalize across failure identities, not only average rates.

## Exact-match sensitivity

Under exact match, SmolLM2 EAR@K is 25% versus 17% for Qwen1.5B, a paired difference of +8 points (−2 to +18). Persistent EAR differs by +7 points (−2 to +16). The k=5→10 EAR difference remains positive at +7 points (+2 to +13), and Accuracy@10 remains 16 points lower (−27 to −5).

The deep-context conclusion survives; the overall family-rate estimate remains uncertain.

## Interpretation boundary

This is one 100-question sample, one lexical ranking, and one quantization per family. Family, tokenizer, training data, alignment, and parameter count differ together, so the comparison does not identify a causal architectural effect. It supports cross-family reproducibility of the EAR phenomenon and motivates the preregistered next step: change the retriever while holding a model fixed.

Machine-readable estimates are in [`comparison.json`](comparison.json), question membership is in [`reversal_set_membership.csv`](reversal_set_membership.csv), and exact-match results are in [`exact_match_sensitivity/`](exact_match_sensitivity/).

# Secondary paired Qwen2.5 0.5B versus SmolLM2 1.7B result card

## Design

This is the preregistered secondary cross-family comparison on the exact same 100 questions and frozen protocol. Qwen2.5 0.5B is exploratory because model family and scale change together; Qwen2.5 1.5B remains the primary comparator.

## Results

| Metric | Qwen0.5B | SmolLM2 | SmolLM2 − Qwen | Paired 95% CI |
|---|---:|---:|---:|---:|
| Accuracy@1 | 23% | 25% | +2 pp | −6 to +10 pp |
| Accuracy@2 | 22% | 30% | +8 pp | −1 to +18 pp |
| Accuracy@3 | 27% | 24% | −3 pp | −14 to +8 pp |
| Accuracy@5 | 27% | 24% | −3 pp | −13 to +7 pp |
| Accuracy@10 | 32% | 18% | −14 pp | −25 to −4 pp |
| EAR@K | 23% | 32% | +9 pp | −1 to +19 pp |
| Persistent EAR | 12% | 21% | +9 pp | +1 to +17 pp |
| Adjacent EAR | 6.25% | 9% | +2.75 pp | −0.5 to +6 pp |
| Adjacent BCR | 8.5% | 7.25% | −1.25 pp | −4.5 to +1.75 pp |

Fourteen questions reverse under both models, 9 only under Qwen0.5B, and 18 only under SmolLM2 (Jaccard 0.341). Exact match preserves the direction: SmolLM2 EAR@K is 25% versus 19% (+6 points, −3 to +16), and persistent EAR is 18% versus 10% (+8 points, 0 to +16).

## Interpretation boundary

The positive persistent-EAR interval is evidence for this paired sample, not proof that SmolLM2 generally reverses more than Qwen. Model family and size are confounded, multiple endpoints are reported, and the sample is exploratory. The result complements—but does not replace—the size-near primary comparison.

Machine-readable estimates are in [`comparison.json`](comparison.json), membership is in [`reversal_set_membership.csv`](reversal_set_membership.csv), and exact-match results are in [`exact_match_sensitivity/`](exact_match_sensitivity/).

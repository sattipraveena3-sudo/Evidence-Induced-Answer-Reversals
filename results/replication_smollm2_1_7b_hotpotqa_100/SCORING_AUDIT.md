# SmolLM2 1.7B scoring audit

## Scope and mechanical checks

The audit covers all 500 saved answers from the 100-question, five-depth SmolLM2 condition. Every primary `correct` label was recomputed from the raw answer and frozen reference using normalized contiguous whole-token containment. There were **zero label mismatches**, all 100 ordered IDs/questions/references matched the Qwen2.5 1.5B comparator, every trajectory used depths 1/2/3/5/10, and all saved runtime metadata matched the frozen contract.

The manual audit was performed after generation by one non-blinded reviewer. The frozen primary labels and metrics were not edited.

## Containment-positive, exact-negative outputs

There were 14 distinct candidate outputs across 11 questions that containment accepted and normalized exact match rejected.

| ID | Depth(s) | Classification | Audit note |
|---|---|---|---|
| `5ae09d61…` | 1,2,3,5 | Valid expansion | “dark comedy-drama” directly contains and refines “comedy-drama.” |
| `5adfb4b8…` | 3 | Valid expansion | Directly states that both works are operas. |
| `5abc32cb…` | 10 | Valid expansion | Direct answer is Karen O. |
| `5a718467…` | 2,10 | Valid expansion | Direct answer is Mazda. |
| `5a718467…` | 3 | Valid expansion | Identifies Mazda and its GF platform. |
| `5a7fd730…` | 5 | Valid expansion | Names both required films; the sentence is truncated after the answer. |
| `5adf4ba6…` | 5 | Valid expansion | Direct answer is Beauty and the Beast. |
| `5a7458ff…` | 1 | Clear false positive | Calls both films “comedy science fiction”; the shared science-fiction claim is false. |
| `5a7458ff…` | 10 | Clear false positive | Repeats the same false shared science-fiction classification. |
| `5abbe09d…` | 1 | Clear false positive | Mentions R.E.M. only as context and answers Michael Stipe instead of what he founded. |
| `5ae701b2…` | 10 | Valid expansion | Direct answer is 1961. |
| `5a86f204…` | 1 | Valid expansion | Direct answer is Secretariat. |
| `5a86f204…` | 2 | Mixed | Direct movie title is correct, but the extra sentence incorrectly names the horse as Tammany. |
| `5ae2196b…` | 5 | Valid expansion | Direct profession is American attorney. |

Totals: **10 valid expanded answers, 3 clear false-positive outputs across 2 questions, and 1 mixed output** with a correct direct answer plus an erroneous extra detail.

## Primary reversal review

All 32 primary containment-scored reversal trajectories were inspected in full.

- **30/32** have an unambiguous correct answer immediately before at least one scored reversal.
- **27/32** contain at least one clearly incorrect answer after a genuinely correct earlier answer.
- Two trajectories (`5a7458ff…` and `5abbe09d…`) begin from clear containment false positives and should not be treated as human-validated harmful reversals.
- `5ae32941…` changes from the full name “Thomas Penson De Quincey” to the correct abbreviated name “Thomas De Quincey”; this is a scoring artifact, not a substantive reversal.
- `5ae2196b…` changes from “American attorney” to “lawyer”; this is semantically equivalent and not a substantive reversal.
- `5abb1e1b…` changes from “Nobel Prize in Literature” to “Nobel Prize.” The shorter answer is underspecified but plausibly acceptable in context, so this trajectory is ambiguous.
- `5adfb4b8…` is timing-sensitive: containment labels “opera compositions” correct and “all operas” incorrect because of singular/plural mismatch, although both are semantically correct. The later k=10 composer answer is clearly wrong, so the question still has genuine trajectory-level degradation, but its scored first-reversal depth and adjacent event are not semantically reliable.

This review shows that the answer-span rule overstates some individual events, but the signal is not explained by those cases: normalized exact match still yields EAR@K 25% (95% CI 17%–34%), persistent EAR 18% (11%–26%), and median first-reversal depth 5.

## Interpretation boundary

The audit is a transparent single-reviewer sensitivity check, not a blinded multi-annotator adjudication. Exact match is conservative and also rejects many legitimate expanded answers. Publication-level work should add aliases or blinded semantic labels, report agreement, and retain both frozen automatic metrics and human-adjudicated sensitivity results.

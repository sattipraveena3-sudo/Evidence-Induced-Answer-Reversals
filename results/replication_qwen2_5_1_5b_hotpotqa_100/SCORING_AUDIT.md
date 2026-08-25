# Post-hoc scoring audit

## Scope and method

The preregistered primary rule marks an answer correct when the normalized reference answer appears as a contiguous whole-token sequence in the normalized model output. Exact match is the preregistered sensitivity rule.

After the run, one non-blinded reviewer inspected **every distinct candidate output accepted only by containment and not by exact match**: 17 strings across 13 questions. The reviewer also inspected all 22 primary reversal trajectories. Saved answers and frozen primary labels were not changed.

## Complete containment-only output audit

| ID | Depths | Verdict | Output or rationale |
|---|---|---|---|
| `5ae09d6155429945ae9593d4` | 1, 10 | Valid expanded answer | `dark comedy-drama` contains the more specific correct genre. |
| `5ae09d6155429945ae9593d4` | 2, 3 | Valid expanded answer | Capitalization variant of `dark comedy-drama`. |
| `5a7cfea2554299452d57babe` | 2, 3, 10 | Valid sentence answer | Correct title followed by “aired first.” |
| `5a73595055429901807dafd6` | 2, 3, 5, 10 | Valid sentence answer | Correct birth date embedded in a grammatical sentence. |
| `5a87defa5542993e715abfec` | 5, 10 | Valid expanded answer | `Gambino family boss John Gotti`. |
| `5a845e9055429933447460ec` | 10 | Valid sentence answer | Correctly states that Buddy Hield plays for the Sacramento Kings. |
| `5a7a2dac5542990198eaf0b6` | 1, 2, 3, 5, 10 | **Clear false positive** | Says Moya Brennan is younger; the reference answer is Keisuke Kuwata, whose name appears only as the rejected alternative. |
| `5ab959905542996be2020497` | 2, 3, 5, 10 | Valid expanded answer | Correct year range followed by “model years.” |
| `5a78f59755429970f5fffdf8` | 2, 3, 5, 10 | Valid sentence answer | Correct comparison winner followed by the predicate. |
| `5a86f204554299211dda2b60` | 2 | Valid direct answer with flawed modifier | Names the requested film as `Secretariat`, although it incorrectly calls Tammany the horse chronicled. |
| `5a86f204554299211dda2b60` | 5, 10 | Valid sentence answer | Correctly names the film `Secretariat` and year. |
| `5a7244955542990c210a408a` | 3 | **Ambiguous indirect match** | Mentions J35 as the engine modified into J71, but the grammatical “name was changed to” answer is J71. This is not a reliable direct short-answer match. |
| `5a8d7f2b554299068b959d0c` | 2 | Valid sentence answer | Correctly names the Liberal Party. |
| `5a78a7025542990784727710` | 1 | Valid sentence answer | Correctly states Jean-Marie Pfaff is older than Anne Noe. |
| `5a78a7025542990784727710` | 2 | Valid sentence answer | Correct comparison winner followed by “is older.” |
| `5a78a7025542990784727710` | 3, 5, 10 | Valid sentence answer | Correctly states Jean-Marie Pfaff is older than Anne Noë. |
| `5ae375955542990afbd1e15d` | 2 | Valid expanded answer | Names the deadpan sketch group and its show. |

The two questionable cases have different effects:

- The clear Keisuke Kuwata/Moya Brennan contradiction is marked correct at all five depths, so it adds one percentage point to candidate accuracy at every depth but creates no transition.
- The ambiguous J35 output at k=3 creates one primary BCR at 2→3 and one primary EAR at 3→5. Of the 22 primary reversal questions, the other 21 have an unambiguous correct answer immediately before at least one reversal.

These observations are a post-hoc audit, not a replacement scoring rule. The automatic exact-match sensitivity remains the prespecified conservative check: EAR@K is 17% (95% CI 10%–24%) and persistent EAR is 11% (5%–17%). The reversal signal therefore survives a rule that rejects both questionable outputs, although exact match also rejects valid sentence-form answers.

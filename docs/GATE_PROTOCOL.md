# Evidence-Stability Gate Protocol

## Status

This document fixes the mitigation design before the primary real-model run. The implementation and deterministic smoke path are tested; no mock output is an empirical result.

## Intervention

For each question, the generator answers over one fixed, nested retrieval ranking. The gate maintains the last non-abstained answer as its **stable anchor**.

At retrieval depth (k):

1. Generate the raw candidate from the Top-(k) prefix.
2. Normalize the candidate and anchor using the public scoring normalization.
3. If they match, emit the candidate without calling a verifier.
4. If they differ, compare both answers against the same Top-(k) evidence.
5. Emit the new answer, retain the anchor, or abstain.
6. Update the anchor only after `accept_new`; retaining or abstaining preserves it.

The gate never receives a reference answer, correctness bit, or future retrieval prefix.

## Verifiers

### Deterministic lexical baseline

For each candidate, compute the largest within-passage fraction of normalized answer tokens supported by any current passage. An exact normalized phrase match receives support 1.0.

Pre-registered defaults:

- support threshold: 0.8
- comparative margin: 0.2
- accept when new support crosses the threshold and exceeds previous support by the margin
- retain when previous support crosses the threshold and exceeds new support by the margin
- abstain otherwise

This is a transparent baseline, not an entailment model.

### Model verifier

Use a fixed prompt that presents the question, previous answer, new answer, and current evidence. The verifier must return one JSON object containing:

- `decision`: `accept_new`, `retain_previous`, or `abstain`
- `previous_support`: number from 0 to 1
- `new_support`: number from 0 to 1
- `reason`: one short evidence-based sentence

The verifier uses no external knowledge by instruction. Invalid decision labels, missing JSON, or out-of-range support values fail the run rather than being silently repaired.

## Comparisons

Every dataset/model/retriever condition must include:

1. no gate
2. lexical gate
3. model gate
4. never-update sanity baseline
5. always-abstain-on-change sanity baseline

The sanity baselines are required because minimizing harmful transitions alone is trivial if the system never accepts new evidence or never answers.

## Primary outcomes

Report at every adjacent depth and overall:

- raw correct-to-incorrect transition rate
- gated correct-to-incorrect **answered** transition rate
- correct-to-abstain rate
- raw and gated beneficial correction rate
- BCR retention
- coverage and selective accuracy at each depth
- final-depth answered accuracy and coverage
- verifier calls per question and per transition
- verifier latency and, when available, token overhead

Use paired question-level bootstrap confidence intervals for raw-versus-gated differences. Keep per-dataset results separate before reporting any macro-average.

## Hypotheses

- **H1:** A comparative-support gate reduces non-abstained harmful transitions relative to no gate.
- **H2:** A useful gate retains a substantial fraction of beneficial corrections; a lower EAR with collapsed BCR is not a success.
- **H3:** Change-triggering invokes the verifier on a minority of depth transitions, reducing overhead relative to verification at every depth.
- **H4:** The model verifier improves the harm/repair/coverage trade-off over the deterministic lexical baseline.

All four hypotheses remain unconfirmed until real-model outputs exist.

## Execution stages

### Pilot

- HotpotQA distractor development split
- 100 questions
- fixed deterministic ranking
- depths 1, 2, 3, 5, and 10
- temperature 0
- lexical gate first, then model gate

The pilot validates data contracts, failure modes, and cost estimates. It is not the final paper result.

### Primary study

- 500–1000 questions per dataset
- at least two open QA datasets
- BM25 and one open dense retriever
- at least two open-weight instruction-model families
- fixed prompts and deterministic decoding where supported
- all raw trajectories and gate metadata retained

## Claim guardrails

- Never use mock trajectories as research evidence.
- Never tune gate thresholds on the primary evaluation questions.
- Never hide abstentions inside the incorrect class when presenting mitigation results.
- Never claim answer instability itself is novel.
- Do not call the gate effective until paired real-model comparisons include EAR, BCR, coverage, and uncertainty.

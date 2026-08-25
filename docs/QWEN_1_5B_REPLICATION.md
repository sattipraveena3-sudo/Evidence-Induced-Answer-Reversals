# Preregistered Qwen2.5 1.5B scale replication

**Frozen before generation:** 2026-08-25T20:06:33Z  
**Status at freeze:** no Qwen2.5-1.5B answers had been generated or inspected for this study.

## Purpose and boundary

This condition tests whether the harmful-reversal signal observed in the 0.5B exploratory pilot survives a threefold increase in parameter count while the sample, ranking, prompts, decoding, scoring, and gate remain fixed. It is a **within-family model-scale replication**. It does not satisfy the planned requirement for a second independent model family or a second retriever.

## Frozen condition

- The exact 100 HotpotQA distractor-development questions from the published pilot, in the same order; prepared-sample SHA-256 `915d6b5706981b0f76e13bd56e3b81f8e09d11be09fd44ad1aa405aadb99f424`.
- The same deterministic lexical-overlap ranking and fixed prefix depths 1, 2, 3, 5, and 10.
- Official `Qwen/Qwen2.5-1.5B-Instruct-GGUF`, revision `91cad51170dc346986eccefdc2dd33a9da36ead9`, file `qwen2.5-1.5b-instruct-q4_k_m.gguf`, SHA-256 `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`.
- `llama-cpp-python==0.3.35`, CPU inference, temperature 0, seed 7, context 4096, batch 512, 9 threads, and at most 32 new tokens.
- Primary binary scoring: normalized contiguous whole-token answer containment. Token F1 is continuous. Normalized exact match is a sensitivity analysis.
- The unchanged lexical gate uses support threshold 0.8 and margin 0.2 and never sees gold labels.
- Question-level bootstrap: 3,000 resamples, seed 7. All comparative intervals are paired on question ID. Adjacent-transition comparisons resample whole question trajectories, not individual transitions.

The machine-readable contract is in [`configs/replication_qwen2_5_1_5b_hotpotqa_100.json`](../configs/replication_qwen2_5_1_5b_hotpotqa_100.json).

## Hypotheses and reporting

The primary falsifiable hypothesis is that at least one correct-to-incorrect adjacent-depth transition occurs in the 1.5B condition. The size-direction comparison is two-sided: no direction is preregistered for the difference in EAR@K, persistent EAR, accuracy, EAR, or BCR.

Report every primary and secondary endpoint even if the run finds no reversal or contradicts expectations. Report the lexical gate's answered harm, abstentions, BCR retention, coverage, and selective accuracy together; reduced answered harm alone is not a mitigation success.

## Paired comparison plan

Compare the new condition with the published 0.5B pilot on the identical IDs:

1. Accuracy and token F1 at every retrieval depth.
2. EAR@K, persistent EAR, and first-reversal depth.
3. Per-question reversal-set discordance and Jaccard overlap.
4. Adjacent-transition EAR and BCR, using question-clustered paired bootstrap differences.
5. Gate coverage, answered accuracy, harmful transitions, and BCR retention as descriptive diagnostics.

No prompt, threshold, scoring rule, sample, or depth may be changed after observing results under this preregistration. Any deviation or replacement run must be recorded in the final manifest and result card.

## Publication provenance

The condition was frozen in local Git object `38c40aa6c9e4f030f73524a3b5c96732119c369e` and the paired-analysis implementation in `ee13853f4d0d652fbf19badd77346ef67063eb80` before generation. The connected GitHub transport later recreated content-identical tree snapshots as public commits `be12be3b8499a95ce6a1c4a64c614396fff4a267` and `74484164ee4a0c5949bf32ff5dafcb19ef97423b`. Consequently, the public commit dates record post-run publication rather than an independent public preregistration timestamp. The result manifest preserves this distinction.

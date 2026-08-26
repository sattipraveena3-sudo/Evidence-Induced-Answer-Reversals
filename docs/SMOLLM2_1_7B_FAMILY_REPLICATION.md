# Preregistered SmolLM2 1.7B independent-family replication

**Frozen before generation:** 2026-08-26T00:52:09Z  
**Status at freeze:** no SmolLM2 answers had been generated or inspected for this study.

## Purpose and boundary

This condition tests whether Evidence-Induced Answer Reversals (EAR) survive a change from the Qwen2.5 family to the independently trained SmolLM2 family while the questions, evidence ranking, nested prefixes, prompt, decoding, scoring, gate, and analysis remain fixed. SmolLM2 1.7B is close in parameter count to the completed Qwen2.5 1.5B condition, so that condition is the primary paired comparator. The Qwen2.5 0.5B pilot is a prespecified secondary comparator.

This is an **independent model-family diagnostic replication**, not a controlled causal estimate of architecture or training effects. Model family, parameter count, tokenizer, training data, alignment recipe, and quantization implementation are not independently manipulated.

## Frozen condition

- The exact 100 HotpotQA distractor-development questions from the two published Qwen conditions, in the same order; prepared-sample SHA-256 `915d6b5706981b0f76e13bd56e3b81f8e09d11be09fd44ad1aa405aadb99f424`.
- The same deterministic lexical-overlap ranking and fixed prefix depths 1, 2, 3, 5, and 10.
- Official Hugging Face repository `HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF`, pinned model-file revision `6a7e79393ef2957e087f11fce1e50476799e313c`, file `smollm2-1.7b-instruct-q4_k_m.gguf`, size 1,055,609,536 bytes, SHA-256 `decd2598bc2c8ed08c19adc3c8fdd461ee19ed5708679d1c54ef54a5a30d4f33`.
- `llama-cpp-python==0.3.35`, CPU inference, temperature 0, seed 7, context 4096, batch 512, 9 threads, and at most 32 new tokens.
- Primary binary scoring: normalized contiguous whole-token answer containment. Token F1 is continuous. Normalized exact match is a sensitivity analysis.
- The unchanged lexical gate uses support threshold 0.8 and margin 0.2 and never sees gold labels.
- Question-level bootstrap: 3,000 resamples, seed 7. All comparative intervals are paired on question ID. Adjacent-transition comparisons resample whole question trajectories, not individual transitions.

The machine-readable contract is in [`configs/replication_smollm2_1_7b_hotpotqa_100.json`](../configs/replication_smollm2_1_7b_hotpotqa_100.json).

## Hypotheses and reporting

The primary falsifiable hypothesis is that at least one correct-to-incorrect adjacent-depth transition occurs in the SmolLM2 condition. The family comparison is two-sided: no direction is preregistered for differences in EAR@K, persistent EAR, accuracy, adjacent EAR, or BCR.

Report every endpoint even if the run finds no reversal or conflicts with prior conditions. Report the lexical gate's answered harm, abstentions, BCR retention, coverage, and selective accuracy together; reduced answered harm alone is not a mitigation success.

## Paired comparison plan

Compare SmolLM2 1.7B first with Qwen2.5 1.5B and second with Qwen2.5 0.5B on the identical ordered IDs:

1. Accuracy and token F1 at every retrieval depth.
2. EAR@K, persistent EAR, and first-reversal depth.
3. Per-question reversal-set discordance and Jaccard overlap.
4. Adjacent-transition EAR and BCR, using question-clustered paired bootstrap differences.
5. Gate coverage, answered accuracy, harmful transitions, and BCR retention as descriptive diagnostics.
6. Exact-match rescoring and paired exact-match comparisons as sensitivity analyses.

## Scoring audit plan

After generation, recompute every saved primary correctness label from raw answers. Manually inspect all distinct SmolLM2 outputs accepted only by containment but rejected by exact match, and inspect every primary reversal trajectory. Preserve the frozen metrics; disclose any clear or ambiguous containment false positives and report exact-match sensitivity rather than silently changing the scoring rule.

No prompt, threshold, scoring rule, sample, comparator, or depth may be changed after observing results under this preregistration. Any replacement run must be limited to a documented technical failure, corrupted artifact, or protocol mismatch and must be disclosed in the final manifest and result card.

## Publication provenance

The public GitHub commit containing this file and the machine-readable contract is the independent pre-generation timestamp. Its SHA will be recorded in the completed result manifest. Model download and environment validation may occur before or after publication, but no SmolLM2 answer generation may begin until that public commit is verified on `main`.

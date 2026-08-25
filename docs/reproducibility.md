# Reproducibility

Pilot seed: 7. Generation temperature: 0. Retrieval ranking: deterministic lexical overlap over the ten HotpotQA distractor contexts. Evaluated retrieval depths: 1, 2, 3, 5, 10. The same ranked prefix is reused at every depth.

The lexical gate defaults are support threshold 0.8 and comparative margin 0.2. The model verifier uses the fixed JSON contract in `GATE_PROTOCOL.md`. Both compare candidates using only the current Top-k prefix; neither receives gold answers or future evidence.

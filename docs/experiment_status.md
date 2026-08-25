# Experiment status

## Verified software milestones

- Raw Top-k trajectory generation
- EAR/BCR/RTB/P-EAR/FRD analysis with bootstrap confidence intervals
- Change-triggered stateful gate with accept, retain, and abstain actions
- Gold-label-free deterministic lexical verifier baseline
- Fixed-JSON model-verifier interface for OpenAI-compatible local or hosted endpoints
- Gate analysis that reports harmful answered transitions separately from abstentions
- Nine passing unit tests and a deterministic end-to-end gate smoke run

## Next empirical milestone

Primary pilot target: HotpotQA distractor development set, 100 questions, deterministic lexical-overlap ranking, Top-k depths 1/2/3/5/10, open-weight generator at temperature 0, and the pre-registered comparisons in `GATE_PROTOCOL.md`.

No primary real-model result exists yet. Publishable outputs must come from real model trajectories, never the mock backend.

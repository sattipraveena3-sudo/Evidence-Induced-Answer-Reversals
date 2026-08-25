# Result contract

A measurement run is considered successful only if it produces `summary.json`, `summary.csv`, `transitions.csv`, `trajectory_counts.csv`, `reversal_examples.jsonl`, and publication plots. Required raw metrics are Accuracy@k, F1@k, EAR, BCR, RTB, EAR@K, P-EAR, FRD, and bootstrap 95% confidence intervals.

A mitigation run must additionally produce `gate_summary.json`, `gate_depth_metrics.csv`, `gate_transitions.csv`, and `gate_decisions.csv`. It must report gated harmful answered transitions, correct-to-abstain transitions, BCR retention, coverage, selective accuracy, verifier calls, and latency. A lower EAR without its BCR and coverage trade-offs is not a valid mitigation result.

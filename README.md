# Evidence-Induced Answer Reversals in Retrieval-Augmented Generation

A reproducible research program for measuring and mitigating **Evidence-Induced Answer Reversals (EAR)**: cases where a RAG system answers correctly with a smaller retrieved context and becomes incorrect after more evidence is added.

## Frozen research question

> When retrieved evidence is expanded along a fixed ranking, which answer changes are harmful, why do they persist or recover, and can a change-triggered evidence-stability gate reduce correct-to-incorrect transitions without suppressing incorrect-to-correct repairs?

The first stage of the repository measures answer trajectories. The planned second stage adds a verifier that runs only when an answer changes, then accepts the new answer, retains the earlier answer, or abstains based on comparative evidence support.

- [Research identity and scope](docs/RESEARCH_IDENTITY.md)
- [30-paper literature map](docs/LITERATURE_MAP.md)
- [Complete workshop-style manuscript and literature matrix](paper/README.md)
- [Rendered manuscript PDF](output/pdf/Evidence_Induced_Answer_Reversals_Praveena_Satti.pdf)
- [Pre-registered gate protocol](docs/GATE_PROTOCOL.md)
- [Pre-registered Qwen2.5-1.5B scale replication](docs/QWEN_1_5B_REPLICATION.md)
- [Pre-registered SmolLM2-1.7B independent-family replication](docs/SMOLLM2_1_7B_FAMILY_REPLICATION.md)
- [Current experiment status](docs/experiment_status.md)

**Research status:** three completed matched conditions now provide 1,500 genuine open-weight generations across Qwen2.5 and SmolLM2. All three find harmful reversals. The publicly preregistered SmolLM2 condition has EAR@K 32% (23%–41%); its overall difference from size-near Qwen1.5B remains imprecise, but its k=5→10 EAR is 11 points higher (+5 to +18). The lexical gate still loses too much coverage and too many repairs. The current diagnostic manuscript package is complete and auditable; it is a workshop-style draft, not yet a peer-reviewed publication or the planned multi-retriever confirmatory study. See the [paper package](paper/README.md), [SmolLM2 result card](results/replication_smollm2_1_7b_hotpotqa_100/RESULTS.md), and [primary cross-family comparison](results/comparison_qwen2_5_1_5b_vs_smollm2_1_7b_hotpotqa_100/RESULTS.md).

## Core metrics

- **EAR** — correct → incorrect transition rate
- **BCR** — incorrect → correct transition rate
- **RTB** — Retrieval Transition Balance = BCR − EAR
- **EAR@K** — fraction of questions with at least one reversal by maximum depth
- **P-EAR** — persistent reversals that never recover
- **FRD** — First Reversal Depth

The key identity is:

`Accuracy(k_b) - Accuracy(k_a) = BCR(k_a,k_b) - EAR(k_a,k_b)`

This is why aggregate Top-k accuracy can hide substantial harmful reversals.

## Project layout

```text
src/ear/
  schema.py       Data validation and normalization
  scoring.py      Exact-match and token-F1 scoring
  backends.py     Mock, local GGUF, and OpenAI-compatible model backends
  gate.py         Change detection, lexical baseline, and model verifier
  runner.py       Generate Top-k answer trajectories
  analysis.py     Compute raw and selective-gate metrics + bootstrap CIs
  compare.py      Paired comparison of matched trajectory conditions
  prepare.py      Dataset conversion utilities
scripts/
  run_smoke_test.sh
  run_openai_example.sh
configs/
  experiment.json
data/
  sample.jsonl
tests/
paper/
results/
```

## 1. Smoke test — no API key required

```bash
python -m pip install -e .
ear-run \
  --input data/sample.jsonl \
  --output results/mock_trajectories.jsonl \
  --backend mock \
  --depths 1,2,3,5 \
  --gate lexical

ear-analyze \
  --input results/mock_trajectories.jsonl \
  --outdir results/mock
```

The mock backend is **only for testing the pipeline**. Its numbers must never be used as research findings.

## 2. Free real-model CPU pilot

Install the local inference extra, then run the frozen 100-question HotpotQA pilot:

```bash
python -m pip install -e '.[local]'
scripts/run_free_pilot.sh
```

The script downloads the official Qwen2.5-0.5B-Instruct Q4_K_M GGUF file, verifies its SHA-256 digest, prepares the deterministic HotpotQA sample, generates five-depth trajectories, applies the lexical gate, and writes the analysis outputs. No API key or paid service is required. The published pilot used 9 CPU threads and took 18 minutes 18 seconds for 500 generations.

The committed [manifest](results/pilot_qwen2_5_0_5b_hotpotqa_100/manifest.json), derived tables, and raw trajectories make the pilot auditable. The model weights and full dataset are not committed.

## 3. Independent-family CPU replication

Install the local and plotting extras, then run the frozen SmolLM2 condition:

```bash
python -m pip install -e '.[local,plots]'
scripts/run_smollm2_1_7b_replication.sh
```

The script verifies the official pinned SmolLM2 1.7B Q4_K_M model, reproduces the exact sample, generates 500 trajectories, and creates primary/secondary paired and exact-match analyses. The committed [result card](results/replication_smollm2_1_7b_hotpotqa_100/RESULTS.md), [scoring audit](results/replication_smollm2_1_7b_hotpotqa_100/SCORING_AUDIT.md), and [manifest](results/replication_smollm2_1_7b_hotpotqa_100/manifest.json) expose raw outputs, uncertainty, trade-offs, provenance, and known scoring failures.

## 4. Real experiment with an OpenAI-compatible endpoint

Set credentials locally:

```bash
export OPENAI_API_KEY="YOUR_KEY"
```

Run:

```bash
ear-run \
  --input data/your_dataset.jsonl \
  --output results/trajectories.jsonl \
  --backend openai \
  --model gpt-4.1-mini \
  --depths 1,2,3,5,10 \
  --limit 500 \
  --gate model
```

Then:

```bash
ear-analyze \
  --input results/trajectories.jsonl \
  --outdir results/primary
```

For two conditions run on the identical questions and depths:

```bash
ear-compare \
  --baseline results/baseline/trajectories.jsonl \
  --candidate results/candidate/trajectories.jsonl \
  --outdir results/comparison \
  --baseline-label baseline \
  --candidate-label candidate
```

The comparison command enforces identical ordered IDs, questions, answers, and retrieval depths, then reports paired question-level bootstrap intervals. Adjacent-transition aggregates resample whole trajectories so the four transitions from one question are not treated as independent.

## Input format

Each JSONL line:

```json
{
  "id": "q1",
  "question": "Who wrote The Trial?",
  "answers": ["Franz Kafka", "Kafka"],
  "passages": [
    "Rank-1 passage",
    "Rank-2 passage",
    "Rank-3 passage"
  ]
}
```

**Important:** `passages` must be one fixed retrieval ranking. Top-5 must be the exact Top-3 prefix plus two additional passages.

## Evidence-stability gate

The gate keeps the last non-abstained answer as a stable anchor. At each larger retrieval depth:

1. If the normalized candidate answer is unchanged, the verifier is not called.
2. If the answer changes, the verifier compares the anchor and candidate using only the current evidence.
3. The verifier returns `accept_new`, `retain_previous`, or `abstain`.
4. An abstention does not erase the last stable anchor, so later evidence can still repair the answer.

Two verifier modes are implemented:

- `--gate lexical` is a deterministic, gold-label-free comparative-support baseline.
- `--gate model` uses the same OpenAI-compatible completion backend with a fixed JSON decision contract. The endpoint can be a local or free-notebook-hosted open model; the core study does not require a paid API.
- `--gate never-update` and `--gate always-abstain` are sanity baselines that expose trivial ways to suppress harmful transitions.

Neither verifier receives the reference answer or correctness label. Gate analysis reports incorrect-answer transitions and correct-to-abstain transitions separately, alongside BCR retention, coverage, selective accuracy, call rate, and latency. This prevents abstention from being misreported as a free reliability improvement. See the [gate protocol](docs/GATE_PROTOCOL.md).

The default `contains` correctness rule means normalized **whole-token-sequence** containment, not arbitrary string-substring matching. For example, the answer `no` does not match `unknown`. Token F1 is always reported alongside the binary trajectory labels.

## Publication protocol

Recommended primary run:

- 500–1000 questions per dataset
- retrieval depths: 1, 2, 3, 5, 10
- deterministic generation (`temperature=0`)
- at least two QA datasets
- ideally two model families and two retrievers
- bootstrap 95% confidence intervals
- retain all C→W examples for qualitative analysis
- never report mock or synthetic numbers as empirical findings

## Closest prior work and novelty boundary

Recent work already studies retrieval-size robustness, correct/wrong transitions under grounding perturbations, sufficient-context abstention, conflict handling, and adaptive retrieval. This project therefore does **not** claim that answer instability alone is new. Its testable contribution is the combined study of fixed-ranking adjacent-depth trajectories, persistence/recovery, and a change-triggered evidence gate that reduces EAR while retaining BCR. See the [literature map](docs/LITERATURE_MAP.md) for the required comparisons.

## Generated outputs

- `summary.json` — machine-readable metrics
- `summary.csv` — table-ready results
- `transitions.csv` — EAR/BCR/RTB per depth transition
- `reversal_examples.jsonl` — all observed C→W examples
- `trajectory_counts.csv` — trajectory taxonomy counts
- `gate_summary.json` — raw-versus-gated reliability and coverage trade-offs
- `gate_depth_metrics.csv` — coverage and selective accuracy at each depth
- `gate_transitions.csv` — raw EAR/BCR versus gated harm, repair, and abstention
- `gate_decisions.csv` — initial, unchanged, accept, retain, and abstain counts
- `manifest.json` — dataset, model, runtime, scoring, and artifact hashes
- `comparison.json` / `comparison.csv` — paired condition differences and intervals
- `reversal_set_membership.csv` — shared and condition-specific reversal IDs

If matplotlib is installed, `ear-analyze --plots` also writes publication-ready PNG figures.

## Result requirement

The three diagnostic conditions establish feasibility and cross-family signal reproducibility; they do not make the repository publication-complete. Publishable prevalence and mitigation claims require the preregistered second-retriever condition and larger multi-model, multi-retriever primary matrix. All empirical claims must come from real model trajectories, never the mock backend.

# Frozen Research Identity

## Field

**Reliable retrieval-augmented language systems**

## One-sentence identity

I study reliability in retrieval-augmented language systems: how changes in retrieved evidence cause answer reversals, and how evidence-aware verification and abstention can prevent harmful transitions.

This sentence is the filter for future research choices. A new paper, experiment, or system belongs in the central research narrative only if it helps **measure, explain, or mitigate evidence-induced instability**. Agentic systems are a later application setting, not a second research identity.

## Flagship program

**From Measurement to Mitigation of Evidence-Induced Answer Reversals in RAG**

### Flagship research question

> When retrieved evidence is expanded along a fixed ranking, which answer changes are harmful, why do they persist or recover, and can a change-triggered evidence-stability gate reduce correct-to-incorrect transitions without suppressing incorrect-to-correct repairs?

### Why this formulation

Aggregate accuracy can improve even while some individually correct answers become wrong. The primary unit of analysis is therefore the **answer trajectory for one question across nested retrieval depths**, not only average accuracy at each depth.

The project deliberately has two halves:

1. **Measurement and diagnosis:** quantify adjacent-depth transitions, persistence, recovery, and associations with retrieval depth, relevance, conflict, order, and answer support.
2. **Mitigation:** invoke a verifier only when the answer changes. The gate decides whether to accept the new answer, retain the earlier answer, or abstain based on comparative evidence support.

## Scope boundaries

### In scope

- Open-domain and multi-hop question answering
- Fixed, nested retrieval rankings at depths such as 1, 2, 3, 5, and 10
- Sparse and dense retrievers
- At least two model families
- Correct-to-incorrect and incorrect-to-correct transitions
- Persistent reversal, recovery, conflict, and evidence-support analysis
- Selective verification, answer retention, and abstention

### Out of scope for the first paper

- Medical imaging and multimodal time-series modeling
- General AI safety or generic hallucination detection
- Training a new foundation model
- Broad agent orchestration benchmarks
- Production latency optimization beyond reporting gate overhead

These topics may provide earlier evidence of engineering ability, but they do not define this research program.

## Contribution ladder

The work should be claimed in this order, and only after evidence exists:

1. **Reproducible trajectory benchmark:** fixed rankings, deterministic generation, public schemas, and confidence intervals.
2. **Transition analysis:** harmful reversals, beneficial corrections, persistence, recovery, and first-reversal depth.
3. **Mechanism analysis:** controlled relevance, contradiction, formatting, order, and context-size factors.
4. **Evidence-stability gate:** a change-triggered verifier that reduces harmful transitions while preserving beneficial corrections.
5. **Agentic extension:** test the same transition framework when an agent repeatedly retrieves evidence.

## Required comparisons

The project must compare against the closest prior work rather than presenting answer transitions as entirely new:

- Retrieval size robustness and no-degradation metrics
- Correct-to-incorrect transition metrics under spurious grounding features
- Non-RAG and fixed-Top-k baselines
- Sufficient-context selective generation
- Retrieval filtering or compression
- Adaptive stopping and conflict-aware RAG methods

## Success criteria

A mitigation result is useful only if it reports both sides of the trade-off:

- reduction in Evidence-Induced Answer Reversals (EAR)
- retained Beneficial Correction Rate (BCR)
- net Retrieval Transition Balance (RTB)
- final answer accuracy and abstention coverage
- verifier calls, latency, and token overhead
- bootstrap confidence intervals and per-dataset results

Optimizing EAR alone is invalid because a system could avoid reversals simply by never accepting new evidence.

## Zero-budget execution path

- Use open datasets and public retrieval corpora.
- Use BM25 plus one open dense retriever.
- Run small open-weight instruction models on available local hardware or free notebook compute.
- Keep the mock backend only for software testing; never report it as an empirical result.
- Pre-register the model, retriever, prompt, depths, sample size, and scoring rules before the primary run.
- Publish code, fixed rankings, trajectory outputs where licensing permits, and analysis tables.

No paid API is required for the core study. A closed model can be added later only as an optional comparison.

## Portfolio relationship

The supporting portfolio should reinforce one of three capabilities:

1. **Retrieval:** Castorini contributions, hybrid search, clinical-trial matching, and repository-aware retrieval.
2. **Verification:** PraxisMesh policy gates and independent postcondition checks.
3. **Reproducible systems:** tests, packaging, observability, controlled execution, and documented limitations across engineering projects.

These capabilities support the flagship; they are not separate doctoral agendas.

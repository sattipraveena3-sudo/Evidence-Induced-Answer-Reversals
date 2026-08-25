# Literature Map: Evidence-Induced Answer Reversals in RAG

## What “20–30 paper literature map” means

It means a structured map **of 20–30 existing papers**, not a plan to write 20–30 papers. The map identifies what is already known, the closest overlaps, required baselines, and the remaining defensible research gap.

This working map contains 27 primary papers. It is intentionally narrower than a general RAG survey and should be updated before any novelty claim.

## A. Foundations and experimental substrate

| Paper | What it establishes | Use in this project |
|---|---|---|
| [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401) | Canonical parametric plus non-parametric RAG formulation. | Foundation and terminology. |
| [Retrieval Augmented Language Model Pre-Training (Guu et al., 2020)](https://proceedings.mlr.press/v119/guu20a.html) | Jointly learned retrieval during language-model pretraining. | Contrasts trained retrieval with black-box in-context RAG. |
| [Dense Passage Retrieval for Open-Domain Question Answering (Karpukhin et al., 2020)](https://arxiv.org/abs/2004.04906) | Dense dual-encoder retrieval for open-domain QA. | Dense-retrieval baseline and ranking source. |
| [Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering (Izacard and Grave, 2020)](https://arxiv.org/abs/2007.01282) | Fusion-in-Decoder and gains from aggregating many passages. | Important counterpoint: average gains can coexist with sample-level reversals. |
| [In-Context Retrieval-Augmented Language Models (Ram et al., 2023)](https://arxiv.org/abs/2302.00083) | RAG by prepending retrieved documents to an unchanged LM. | Matches the black-box/API-compatible setting. |
| [HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering (Yang et al., 2018)](https://aclanthology.org/D18-1259/) | Multi-hop QA with supporting-fact annotations. | Primary dataset candidate for evidence and conflict analysis. |

## B. Context, noise, conflict, and robustness

| Paper | What it establishes | Relationship to the flagship |
|---|---|---|
| [Lost in the Middle (Liu et al., 2024)](https://arxiv.org/abs/2307.03172) | Use of evidence depends on its position in long context. | Motivates order controls and position-sensitive reversal analysis. |
| [Large Language Models Can Be Easily Distracted by Irrelevant Context (Shi et al., 2023)](https://proceedings.mlr.press/v202/shi23a.html) | Irrelevant inputs can sharply reduce reasoning accuracy. | Motivates controlled distractor conditions. |
| [Making Retrieval-Augmented Language Models Robust to Irrelevant Context (Yoran et al., 2024)](https://openreview.net/forum?id=ZS4m74kZpH) | Analyzes when retrieval reduces QA accuracy and studies filtering/robust training. | Close overlap; required filtering baseline. |
| [The Power of Noise (Cuconasu et al., 2024)](https://arxiv.org/abs/2401.14887) | Passage relevance, position, and count interact in non-obvious ways. | Requires separating random noise from plausible but misleading retrieval. |
| [How Easily do Irrelevant Inputs Skew the Responses of Large Language Models? (Wu et al., 2024)](https://arxiv.org/abs/2404.03302) | Builds graded semantically related irrelevant contexts and tests robustness. | Supplies a distractor taxonomy for mechanism experiments. |
| [Benchmarking Large Language Models in Retrieval-Augmented Generation / RGB (Chen et al., 2023)](https://arxiv.org/abs/2309.01431) | Evaluates noise robustness, negative rejection, information integration, and counterfactual robustness. | Required diagnostic benchmark and taxonomy comparison. |
| [Evaluating the Retrieval Robustness of Large Language Models (Cao et al., 2025)](https://arxiv.org/abs/2505.21870) | Defines no-degradation, retrieval-size, and retrieval-order robustness under realistic RAG. | **Closest depth-based overlap.** The flagship must add adjacent trajectory taxonomy, persistence/recovery, and mitigation—not repackage retrieval-size robustness. |
| [Quantifying the Robustness of Retrieval-Augmented Language Models Against Spurious Features in Grounding Data (Yang et al., 2025)](https://arxiv.org/abs/2503.05587) | Measures sample-level correct/wrong transitions under semantic-agnostic grounding perturbations. | **Closest transition-metric overlap.** Differentiate fixed nested rankings from synthetic feature perturbations and compare metrics directly. |
| [Sufficient Context: A New Lens on Retrieval Augmented Generation Systems (Joren et al., 2025)](https://openreview.net/forum?id=Jjr2Odj8DJ) | Studies whether retrieved context is sufficient and uses that signal for selective generation. | Strong baseline for abstention and evidence sufficiency. |
| [Retrieval-Augmented Generation with Conflicting Evidence (Wang et al., 2025)](https://openreview.net/forum?id=z1MHB2m3V9) | Benchmarks RAG under conflicting evidence and proposes conflict handling. | Baseline for conflict-induced reversals and verification. |

## C. Evaluation, faithfulness, and abstention

| Paper | What it establishes | Use in this project |
|---|---|---|
| [RAGAS: Automated Evaluation of Retrieval Augmented Generation (Es et al., 2023)](https://arxiv.org/abs/2309.15217) | Reference-free component metrics for RAG evaluation. | Secondary evaluation only; exact-match/F1 remain primary for transitions. |
| [ARES: An Automated Evaluation Framework for RAG Systems (Saad-Falcon et al., 2024)](https://aclanthology.org/2024.naacl-long.20/) | Judges context relevance, answer faithfulness, and answer relevance. | Candidate evidence-support signal and evaluator baseline. |
| [RAGTruth (Niu et al., 2024)](https://arxiv.org/abs/2401.00396) | Human-annotated corpus of RAG hallucinations at case and word levels. | Grounds the distinction between answer correctness and faithfulness. |
| [Unanswerability Evaluation for Retrieval Augmented Generation / UAEval4RAG (Peng et al., 2025)](https://aclanthology.org/2025.acl-long.415/) | Evaluates rejection across six unanswerable-query categories. | Required abstention trade-off and coverage comparison. |

## D. Mitigation and adaptive retrieval

| Paper | What it establishes | Use in this project |
|---|---|---|
| [Self-RAG (Asai et al., 2024)](https://openreview.net/forum?id=hSyW5go0v8) | Learns retrieval, generation, and critique with reflection tokens. | Full learned self-critique baseline; heavier than the proposed change-triggered gate. |
| [RECOMP (Xu et al., 2024)](https://openreview.net/forum?id=mlJLVigNHp) | Compresses retrieved context and can selectively omit augmentation. | Filtering/compression baseline for harmful extra evidence. |
| [Corrective Retrieval Augmented Generation (Yan et al., 2024)](https://arxiv.org/abs/2401.15884) | Uses a retrieval evaluator and corrective actions when retrieval quality is poor. | Retrieval-quality gate baseline. |
| [Adaptive-RAG (Jeong et al., 2024)](https://aclanthology.org/2024.naacl-long.389/) | Routes questions among no-retrieval, one-step, and iterative strategies by complexity. | Query-level routing baseline; the flagship gate instead reacts to observed answer change. |
| [Astute RAG (Wang et al., 2025)](https://arxiv.org/abs/2410.07176) | Consolidates internal and retrieved knowledge with source and conflict awareness. | Strong conflict-resolution baseline. |
| [Stop-RAG (Park et al., 2025)](https://arxiv.org/abs/2510.14337) | Learns when to stop iterative retrieval with a value-based controller. | Closest adaptive stopping baseline; compare performance, training cost, and verifier overhead. |
| [Instructing Retrieval-Augmented Generation with Explicit Denoising (Wei et al., 2024)](https://arxiv.org/abs/2406.13629) | Trains RAG systems to produce denoising rationales before answering. | Denoising baseline and failure-analysis comparison. |

## Defensible gap after mapping

The literature does **not** support claiming that correct-to-incorrect answer changes, retrieval-size instability, or selective retrieval are wholly new. The defensible research package is the combination of:

1. fixed nested rankings and adjacent-depth answer trajectories;
2. a unified harmful/beneficial transition, persistence, and recovery analysis;
3. controlled attribution to relevance, conflict, order, and support;
4. a **change-triggered comparative evidence gate** that accepts, retains, or abstains; and
5. explicit optimization of harmful-reversal reduction **without sacrificing beneficial corrections**.

This is a working hypothesis about the gap, not a novelty claim. The claim must be rechecked immediately before submission.

## Minimum baseline matrix

| Family | Baseline |
|---|---|
| Retrieval depth | fixed Top-1/3/5/10 and best validation-selected Top-k |
| Robustness metrics | no-degradation rate, retrieval-size robustness, EAR/BCR/RTB |
| Evidence control | relevance filter or RECOMP-style selective compression |
| Selective answering | sufficient-context gate and calibrated abstention |
| Adaptive control | CRAG-style evaluator and Stop-RAG-style stopping |
| Conflict handling | Astute RAG or conflicting-evidence baseline |

## Reading order

Start with the two closest overlaps—Cao et al. and Yang et al.—then Sufficient Context, Yoran et al., Stop-RAG, and Astute RAG. Read the remaining papers to finalize controls, baselines, and evaluation. For every paper, record the dataset, retriever, model, intervention, metric, result, and limitation in experiment notes.

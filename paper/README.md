# Paper package

**Title:** *When More Retrieved Evidence Makes Answers Worse: A Reproducible Study of Evidence-Induced Answer Reversals*

This directory contains a complete, venue-neutral workshop manuscript built from the repository's three finished real-model conditions. It is a submission-ready research draft, not a claim of peer review, acceptance, or publication.

## Contents

- [`main.tex`](main.tex) — full humanized manuscript
- [`references.bib`](references.bib) — 30 mapped primary papers plus model reports
- [`LITERATURE_MATRIX.csv`](LITERATURE_MATRIX.csv) — sortable 30-paper research map
- [`build_figures.py`](build_figures.py) — regenerates the main figure from committed JSON results
- [`figures/main_results.png`](figures/main_results.png) — generated result figure
- [`../output/pdf/Evidence_Induced_Answer_Reversals_Praveena_Satti.pdf`](../output/pdf/Evidence_Induced_Answer_Reversals_Praveena_Satti.pdf) — final rendered manuscript

## Build

From this directory:

```bash
make
```

The build regenerates the figure, runs BibTeX, compiles the manuscript, and writes the final PDF under `output/pdf/`. It requires Python with matplotlib, `pdflatex`, and `bibtex`.

## Submission checklist

Before sending the paper to a venue:

1. Replace the neutral layout with that venue's official template.
2. Apply the venue's anonymity and supplementary-material rules.
3. Refresh the literature search; the current map was verified on 26 August 2026.
4. Match the title, abstract, author order, and artifact links in the submission form.
5. Keep the current diagnostic scope unless the planned second-retriever and larger primary experiments are completed.

The manuscript intentionally calls the lexical gate a negative diagnostic baseline because it reduces answered harm by abstaining often and suppressing beneficial repairs. That limitation should not be softened in submission materials.

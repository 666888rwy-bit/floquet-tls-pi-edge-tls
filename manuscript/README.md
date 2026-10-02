# Physical Review A Regular Article draft

This directory contains a journal-directed review manuscript and Supplemental Material aligned to the repository's completed Gate A v3 and Gate D2 records. It is an author-review draft, not a claim of editorial acceptance or a submitted version. APS accepts a review PDF and prefers LaTeX source; the single-column XeLaTeX layout is kept to make this Overleaf package self-contained.

## Compile

On Overleaf, upload the manuscript package, select XeLaTeX as the compiler, and set `main.tex` as the main document. To compile the supplement, switch the main document to `supplementary/supplement.tex`. Locally, use XeLaTeX from this directory:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
cd supplementary
latexmk -xelatex -interaction=nonstopmode -halt-on-error supplement.tex
```

The main manuscript is organized in the following evidence order:

1. common physical preparation and response observable;
2. exact finite-system boundary-selective TLS response;
3. drive dependence and limits of a universal topological interpretation;
4. completed response-blind N=4-to-N=6 Gate D2 raw-weight transfer;
5. coupling-resolved hybridization and damping-controlled backaction;
6. channel and multichannel validity diagnostics and breakdown;
7. discussion and conclusion.

The manuscript figures are tracked for a self-contained submission build. Their data and regeneration routes are mapped in `../docs/CLAIM_TO_ARTIFACT.md`. To validate the committed evidence without rerunning expensive propagation, use:

```bash
python scripts/run_submission_checks.py --check-only
```

The platform-independent model schematic can be regenerated without physical propagation:

```bash
python scripts/submission/50_generate_pra_model_figure.py
```

To rebuild the damping/backaction panel directly into this directory from the committed checkpoint, use:

```bash
python scripts/submission/20_generate_damping_figure.py \
  --output-dir manuscript/figures
```

To rebuild the eight-drive transfer and coupling/phase panels from their committed
records, use:

```bash
python scripts/submission/30_generate_d2_transfer_figure.py \
  --output manuscript/figures/fig4_d2_weight_transfer.png
python scripts/submission/40_generate_coupling_figure.py \
  --main-output manuscript/figures/fig3_theory_tested_tls_spectroscopy.png \
  --phase-output manuscript/figures/figS5_detuning_phase.png
```

Do not edit immutable JSON records, frozen protocols, or result manifests to change manuscript presentation. Derived figures belong in `build/` during normal auditing and are included here only as submission assets.

Before submitting, the author should independently verify the final interpretation, citations, title, authorship, affiliation, and AI-use statement. The archival DOI in the data statement has not yet been updated to a version-specific manuscript archive. The `PRA_REVISION_NOTES.md` file records the journal-facing changes and remaining author decisions.

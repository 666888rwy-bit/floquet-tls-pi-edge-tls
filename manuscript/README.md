# Manuscript source

This directory contains the current evidence-first manuscript and Supplementary Material aligned to the repository's completed Gate A v3 and Gate D2 records.

## Compile

Use XeLaTeX from this directory:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
cd supplementary
latexmk -xelatex -interaction=nonstopmode -halt-on-error supplement.tex
```

The main manuscript is organized in the following evidence order:

1. common physical preparation and frozen protocol;
2. exact finite-system boundary-selective TLS response;
3. drive dependence and limits of a universal topological interpretation;
4. completed response-blind N=4-to-N=6 Gate D2 raw-weight transfer;
5. coupling-resolved hybridization and damping-controlled backaction;
6. channel and multichannel validity diagnostics and breakdown;
7. discussion and conclusion.

The manuscript figures are tracked for a self-contained submission build. Their data and regeneration routes are mapped in `../docs/CLAIM_TO_ARTIFACT.md`. To validate all committed evidence without rerunning expensive propagation, use:

```bash
python scripts/run_submission_checks.py --check-only
```

To rebuild the damping/backaction panel directly into this directory from the committed checkpoint, use:

```bash
python scripts/submission/20_generate_damping_figure.py \
  --output-dir manuscript/figures
```

Do not edit immutable JSON records, frozen protocols, or result manifests to change manuscript presentation. Derived figures belong in `build/` during normal auditing and are included here only as submission assets.

# Local Dissipative Probing of Floquet \(\pi\)-Edge Modes by a Two-Level Defect

> **Reviewer-facing research code, compact numerical checkpoints, and figure-regeneration scripts for a finite open Floquet-chain study.**

This repository supports a manuscript in preparation on a dissipative two-level-system (TLS) defect locally coupled to a periodically driven Ising chain. The central question is not whether a thermodynamic time-crystal phase exists, but how a **finite Floquet \(\pi\)-edge response** is locally read out, loaded, and modified by a dissipative TLS.

## Reviewer route

A reviewer can examine the evidence hierarchy without running the long production scans. The compact checkpoints are included, and the key analyses regenerate their own output files under `results/reproduced/`.

| If you want to verify… | Run | Main input | Expected artifact |
|---|---|---|---|
| A two-boundary response-localization fit and its distinction from closed-chain lengths | `python scripts/10_double_boundary_localization.py` | `floquet_tls_N6_position_frequency_checkpoint.npz` | `A_double_boundary_localization_fit.png` |
| The resolved edge-response doublet versus local effective coupling | `python scripts/20_effective_coupling_scaling.py` | `floquet_tls_N6_g_frequency_checkpoint.npz` | `B_response_splitting_vs_geff.png` |
| Independent channel–time-domain validation at \(N=4\) | `python scripts/30_channel_time_validation.py` | Exact channel construction | `C_N4_channel_time_validation.png` |
| The limits of a single-parameter effective-coupling description away from the edge | `python scripts/90_multipo_effective_model_limit.py` | `multipo_center_coarse_checkpoint.npz` | `multipo_center_coarse_spectra.png` |

The complete protocol, output checks, numerical conventions, and known boundaries of inference are in [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md). The shortest manuscript-claim-to-file map is in [docs/REVIEWER_GUIDE.md](docs/REVIEWER_GUIDE.md).

## Repository map

| Path | Purpose |
|---|---|
| `scripts/` | Ordered, standalone analysis entry points. Prefixes `00`, `10`, `20`, `30`, and `90` indicate the recommended reading/execution order. |
| `notebooks/` | Cleaned, output-free research notebooks retaining the full numerical workflow and model definitions. |
| `data/checkpoints/` | Compact `.npz` checkpoints used by the public scripts. See [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md). |
| `results/manuscript_figures/` | Frozen reference images corresponding to the reviewed analysis state. |
| `results/reproduced/` | Regenerated analysis products. These files are intentionally versioned so output comparisons are direct. |
| `docs/` | Reproducibility protocol, reviewer guide, data dictionary, and public-release checklist. |

## Quick start

The supplied scripts have been tested with Python 3.11, NumPy, SciPy, and Matplotlib. Create an isolated environment and install the declared dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To regenerate the three primary reviewer checks in the recommended order, run the single command below from the repository root:

```bash
python scripts/run_reviewer_checks.py
```

The scripts may also be run individually when auditing a specific conclusion:

```bash
python scripts/10_double_boundary_localization.py
python scripts/20_effective_coupling_scaling.py
python scripts/30_channel_time_validation.py
```

The first N=6 reference propagation may be added with `python scripts/run_reviewer_checks.py --include-reference`. It provides a direct numerical implementation check against a saved production checkpoint. The `90_` diagnostic may be added with `--include-limit`; it records an **effective-model limitation**, not a positive multi-position collapse claim.

## What this repository establishes—and what it does not

The included evidence supports boundary-selective TLS spectroscopy, a resolved boundary-response doublet in the stated finite-window regime, a nonmonotonic dissipation crossover, and targeted Floquet-channel evidence. It does **not** establish a thermodynamic-limit time-crystal phase, a sharp dissipative phase boundary, or a universal position-independent \(|g_m|\) collapse. These scope boundaries are deliberate and are described in the reproducibility protocol.

## Citation and data availability

The compact numerical checkpoints required by the public analysis scripts are distributed in this repository. The earlier manuscript preprint is archived on [Zenodo](https://doi.org/10.5281/zenodo.20685212). Please cite the associated manuscript or Zenodo record when using this code, its checkpoints, or derived numerical results. A `CITATION.cff` file should be added once the definitive manuscript title and author list are finalized.

## License

This repository is released under the [MIT License](LICENSE). The license applies to the source code and documentation. The included numerical checkpoints are provided for reproducibility; please retain scientific attribution when reusing them.

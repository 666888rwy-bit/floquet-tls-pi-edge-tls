# Local Dissipative Probing of Floquet π-Edge Modes by a Two-Level Defect

> **Research code and compact numerical checkpoints for a finite open Floquet-chain study.**

This repository accompanies a manuscript in preparation on a dissipative two-level-system (TLS) defect locally coupled to a Floquet Ising chain. It studies how the TLS transverse response probes a finite Floquet π-edge mode, how the response splitting depends on the local effective coupling, and how TLS damping produces a loading-to-elimination crossover.

## Scope and result boundaries

The results concern a **finite**, Markovian Floquet–Lindblad model. They do not establish a thermodynamic-limit time-crystal phase or a universal position-independent effective-coupling collapse. The included N=6 data instead support boundary-selective TLS spectroscopy, a resolved boundary-response doublet, a dissipation crossover, and targeted π-sector channel evidence.

## Repository layout

| Path | Contents |
|---|---|
| `notebooks/` | Cleaned, output-free versions of the four latest research notebooks. |
| `analysis/` | Independent scripts for the N=6 reference point and A/B/C follow-up analyses. |
| `data/checkpoints/` | Compact production `.npz` checkpoint files. |
| `results/figures/` | Selected data-backed figures generated from the included analysis. |
| `docs/` | Reproducibility notes. |

## Quick start

Create an isolated environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For a reference N=6 propagation and checkpoint comparison:

```bash
python analysis/reproduce_n6_reference_point.py
```

For the analysis figures:

```bash
python analysis/a_double_boundary_localization.py
python analysis/b_effective_coupling_scaling.py
python analysis/c_n4_channel_time_validation.py
```

The notebooks document the original parameter scans and channel/position validation workflow. Because all full scans are computationally demanding, the repository ships compact checkpoints for inspection and figure regeneration.

## Data availability

The numerical checkpoints used by the public analysis scripts are included in `data/checkpoints/`. The original manuscript preprint is archived at [Zenodo](https://doi.org/10.5281/zenodo.20685212).

## Citation

If you use this repository, please cite the associated manuscript or Zenodo record. A final citation file and software release tag will be added once the manuscript title, author list, and license are finalized.

## License

This repository is released under the [MIT License](LICENSE). The included compact numerical checkpoints are provided to reproduce the accompanying analyses; please cite the associated manuscript or Zenodo record when using the code or derived results.

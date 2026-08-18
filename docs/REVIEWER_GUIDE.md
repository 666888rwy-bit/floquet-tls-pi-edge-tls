# Reviewer guide: claim-to-evidence map

This guide is a concise audit map for the associated manuscript. It is designed to make the strongest claims reproducible while making the limits of each inference equally visible.

## Recommended 15-minute audit path

Begin with the repository root `README.md`, then run scripts `10`, `20`, and `30` in that order. The sequence first establishes a spatially selective response, then the resolved boundary response splitting, and finally a channel-to-time-domain mechanism check. All three commands use bundled data or exact N=4 construction and avoid a full N=6 production sweep.

| Manuscript-level statement | Evidence artifact | Public command or source | What a reviewer should verify | Boundary of interpretation |
|---|---|---|---|---|
| The TLS acts as a local probe with boundary-enhanced response. | Position–frequency response and two-boundary fit. | `scripts/10_double_boundary_localization.py` using `floquet_tls_N6_position_frequency_checkpoint.npz`. | Response decreases rapidly away from both boundaries; inspect all discard windows. | The fitted response length is not the same as the bare closed-chain edge-mode length. |
| The boundary TLS spectrum has a coupling-resolved doublet. | Peak-pair extraction and \(\Delta\omega_{\rm response}\) versus \(|gB_{0\pi}(0)|\) plot. | `scripts/20_effective_coupling_scaling.py` using `floquet_tls_N6_g_frequency_checkpoint.npz`. | Accepted points show the reported empirical relation; rejected/ambiguous points are not silently included. | The fit has a nonzero intercept and is not a zero-coupling theorem. |
| TLS damping produces a loading-to-elimination crossover. | N=6 damping checkpoint. | `data/checkpoints/floquet_tls_N6_gamma_checkpoint.npz`; associated production notebook. | Compare edge response, TLS response, and emission across damping. | The figure should be called a crossover, not a dissipative phase diagram. |
| A slow \(\pi\)-sector channel pair controls the visible late-time response. | Exact N=4 channel, direct trace fit, and targeted N=6 Arnoldi checkpoint. | `scripts/30_channel_time_validation.py` and `floquet_tls_N6_edge_seeded_pi_arnoldi_v2_checkpoint.npz`. | The time fit is independently initialized and gives the stated approximate channel agreement. | The N=4 agreement is quantitative but not exact; early-time multimode content remains. |
| A one-parameter local effective model has a controlled range of use. | Interior high-bare-coupling diagnostic. | `scripts/90_multipo_effective_model_limit.py`. | Equal target \(|g_m|\) in the interior requires large bare \(g\) and reorganizes the response. | Do not describe this as a successful three-position collapse. |

## What is intentionally included

The repository contains the minimal code and compact data required to inspect the positive results as well as the relevant negative boundary test. It also includes output-free notebooks so that a reader may trace the full model and production workflow. The check-point analyses are separated from expensive direct simulation so that evidence can be audited on ordinary hardware.

## What is intentionally excluded

The repository does not contain old manuscript drafts, obsolete figures, browser-renamed duplicate data files, temporary solver output, credentials, or environment-specific paths. It also does not claim that a limited set of higher-size open-system trajectories would establish a thermodynamic trend; such isolated curves are not part of the evidence hierarchy.

## Figure conventions

`results/manuscript_figures/` contains frozen images for reference. `results/reproduced/` contains the baseline output of the current scripts. A script rerun may overwrite files only in `results/reproduced/`, which makes direct figure comparisons straightforward. For any manuscript revision, preserve the prior generated results in a tagged commit before replacing a figure baseline.

## Minimal reviewer checklist

| Check | Expected outcome |
|---|---|
| `git status --short` after cloning | No output before running scripts. |
| `python scripts/10_double_boundary_localization.py` | Regenerates the A figure and Markdown/JSON summary. |
| `python scripts/20_effective_coupling_scaling.py` | Regenerates the B figure and preserves the nonzero-intercept fit. |
| `python scripts/30_channel_time_validation.py` | Regenerates the C figure and its channel/time comparison table. |
| Inspect `docs/DATA_DICTIONARY.md` | Every compact checkpoint has an explicit intended use and scope boundary. |

> The scientific standard adopted here is transparency rather than overclaiming: each positive statement is paired with a clear computational provenance, and each known limitation is stated in the same repository.

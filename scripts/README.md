# Analysis entry points

The scripts in this directory are deliberately numbered. The ordering is a reading aid rather than an assumption that every production calculation must be repeated from scratch. All relative paths are resolved from the repository root, so invoke the scripts from any working directory using `python path/to/script.py`.

| Script | Computational layer | Primary purpose | Runtime expectation | Output |
|---|---|---|---|---|
| `00_reproduce_n6_reference.py` | Direct propagation | Recompute one N=6 production working point and compare it with the saved checkpoint. | Longest direct propagation in this repository. | Printed numerical comparison. |
| `10_double_boundary_localization.py` | Checkpoint analysis | Fit the N=6 position response to a two-boundary exponential form and compare response and closed-chain lengths. | Seconds. | Figure, Markdown summary, JSON summary. |
| `20_effective_coupling_scaling.py` | Checkpoint analysis | Extract the resolved response splitting and plot it against \(|gB_{0\pi}(0)|\). | Seconds. | Figure, Markdown summary, JSON summary. |
| `30_channel_time_validation.py` | Exact channel plus time-domain fit | Construct the N=4 Floquet channel, identify the selected \(\pi\)-sector pair, and independently fit the raw time trace. | Moderate; exact Liouville-space calculation. | Figure, Markdown summary, JSON summary. |
| `90_multipo_effective_model_limit.py` | Checkpoint analysis | Diagnose why equal target \(|g_m|\) at interior positions requires strong bare coupling and does not yield a clean universal collapse. | Seconds. | Figure and Markdown diagnosis. |

All generated files are written to `results/reproduced/`. Existing reference images in `results/manuscript_figures/` are never overwritten by these scripts.

> **Interpretation rule.** Scripts `10`, `20`, and `30` are the primary analysis path. Script `90` is included to document the tested limitation of an overextended effective-model claim. It should not be cited as evidence for a successful multi-position collapse.

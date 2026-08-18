# Checkpoint data dictionary

This repository distributes **compact derived numerical checkpoints**, rather than raw transient trajectories from every production calculation. Each `.npz` file is loaded with `numpy.load(..., allow_pickle=False)`. Arrays named `completed` are mandatory integrity masks: analyses should never interpret an uncompleted point as a physical zero.

## Shared conventions

| Convention | Meaning |
|---|---|
| `N` | Number of chain spins; the TLS is an additional local degree of freedom. |
| `omega_ratio`, `ratios`, `omega_ratios` | Drive-frequency ratio \(\omega_d/(\Omega/2)\), where unity is the nominal subharmonic resonance condition. |
| `d08`, `d20`, `d40` | Transient-discard windows of 8, 20, and 40 Floquet periods, respectively. |
| `A_edge` | Magnitude of the edge subharmonic phasor. |
| `A_tls` or `A_tls_transverse` | Magnitude of the transverse TLS subharmonic phasor. |
| `Mpi_*` | Stroboscopic \(\pi\)-component diagnostic for the stated observable. |
| `tls_emission` or `emission` | TLS emission proxy, conventionally \(\gamma_1\overline{n}_d\). |
| `relative_phase` or `phase_tls_minus_edge` | TLS phase relative to the edge response under the stated phasor convention. |

## Checkpoint inventory

| File | Sweep axes and size | Main observables | Primary public use |
|---|---|---|---|
| `floquet_tls_N6_position_frequency_checkpoint.npz` | Contact site `sites` (6) × `ratios` (61), with three discard windows | `A_edge`, `A_tls`, `emission`, `relative_phase` | Two-boundary localization fit and boundary-versus-interior response comparison. |
| `floquet_tls_N6_g_frequency_checkpoint.npz` | Bare coupling `g_values` (7) × `omega_ratios` (61), with three discard windows | `A_edge`, `A_tls_transverse`, `tls_emission`, `Mpi_edge_strobe`, relative phase | Resolved peak-pair extraction and effective-coupling scaling. |
| `floquet_tls_N6_gamma_checkpoint.npz` | TLS damping `gamma_values` (31), with three discard windows | `A_edge`, `A_tls_transverse`, `tls_emission`, `Mpi_edge_strobe`, relative phase | Dissipation loading-to-elimination crossover. |
| `floquet_tls_frequency_production_checkpoint.npz` | Frequency `omega_ratio` (61) at one production working point | Edge and TLS phasors, TLS population, emission, phase, stroboscopic diagnostics | Direct spectrum inspection and reference working-point diagnostics. |
| `floquet_tls_open_size_checkpoint.npz` | `N_values` (5) × three selected frequency ratios | `A_edge`, `A_tls_transverse`, `tls_emission` for discard 20 | Finite-size sensitivity check for the local emission readout. |
| `floquet_tls_N6_edge_seeded_pi_arnoldi_v2_checkpoint.npz` | Four completed edge-seeded targets; 40 recorded iteration-history rows | `records`, `history`, corresponding column labels, Arnoldi metadata | Production-scale targeted \(\pi\)-sector channel evidence. |
| `multipo_center_coarse_checkpoint.npz` | Interior sites 1 and 2 × 17 frequency ratios × two discard windows | `A_tls` at matched target effective couplings | Diagnostic showing the limitations of extending the boundary effective model to high bare couplings in the interior. |

## Detailed checkpoint notes

### N=6 position–frequency response

The first dimension of each response array is ordered by `sites`; the second is ordered by `ratios`. For a discard window `dXX`, `A_tls_dXX[site_index, frequency_index]` is the transverse TLS response amplitude. `metadata_N`, `metadata_periods`, `metadata_samples_per_step`, `metadata_g`, and `metadata_gamma1` record the production setting. The public localization script treats the root-integrated TLS amplitude as the primary spatial proxy and uses the other two proxies only as sensitivity checks.

### N=6 coupling–frequency response

Each two-dimensional array is indexed as `[g_index, frequency_index]`. The file supplies `completed[g_index, frequency_index]`, so scripts can reject incomplete work units. `metadata_gamma1`, `metadata_Omega`, and `metadata_T` define the damping, drive scale, and Floquet period used by the scan. The public scaling script extracts a peak pair only when it meets its explicit spectral-resolution acceptance rules.

### N=6 damping scan

Each vector is indexed by `gamma_values`. The damping checkpoint has the same response naming scheme as the coupling-frequency checkpoint and carries `metadata_g` and `metadata_omega_ratio` to identify its fixed working point. It supports a crossover interpretation, not a sharp phase-boundary inference.

### Targeted N=6 \(\pi\)-channel analysis

`records` and `history` are numerical tables. Their column names are included as the Unicode arrays `record_columns` and `history_columns`, respectively; read these labels from the file rather than assuming a fixed column order. `metadata_algorithm`, `metadata_krylov_dim`, `metadata_residual_tol`, and `metadata_report_every` document the targeted Arnoldi protocol. `completed_g` identifies finished coupling targets.

### Coarse interior-position diagnostic

`multipo_center_coarse_checkpoint.npz` contains only the two interior sites required to demonstrate the failure mode of naive multi-position collapse. Its `target_geff` describes the attempted effective coupling, while `g_values` makes clear that matching the edge \(|g_m|\) would require much larger bare couplings in the interior. This dataset must therefore be read as a model-validity diagnostic, not as missing data from a claimed collapse.

## Integrity and provenance

The checkpoint files were selected from the final analysis state and are intentionally small enough to version directly. The repository excludes browser-renamed duplicate files and transient solver output. To make a local checksum manifest, run:

```bash
sha256sum data/checkpoints/*.npz
```

The scripts do not alter any checkpoint. Newly generated figures and summaries are written only to `results/reproduced/`.

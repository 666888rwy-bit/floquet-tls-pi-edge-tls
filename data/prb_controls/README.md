# PRB multichannel-control data

This directory contains compact, machine-readable summaries of formal Floquet--Lindblad truncation controls. It deliberately excludes raw time trajectories and sparse solver intermediates. Use `scripts/41_plot_prb_controls.py` for the fast audit and `scripts/40_formal_k_convergence.py` for a high-cost direct recomputation.

## Files

| File | System and purpose |
|---|---|
| `N6_g0p08_matched_k_convergence.json` | N=6 positive K-convergence anchor under the matched 11-detuning, 80-period/d20 protocol. |
| `N8_g0p08_matched_k_convergence.json` | N=8 representative positive control under the identical protocol. |
| `N8_g0p12_strong_coupling_k_convergence.json` | N=8 strong-coupling control; only \(g\) differs from the N=8 positive anchor. |
| `N6_K4_model_error_anchors.json` | Six N=6 production-protocol K=4 anchors used for the finite-system model-error map. |
| `three_curve_k_convergence_table.csv` | Compact table of the three K-error curves used in the PRB convergence/breakdown summary. |

## Schema for K-convergence JSON files

| JSON field | Meaning |
|---|---|
| `metadata.N` | Number of Ising-chain spins; the TLS is an additional degree of freedom. |
| `metadata.g`, `metadata.gamma1` | Local exchange coupling and TLS amplitude-damping rate. |
| `metadata.ratios` | The 11 detunings \(\omega_d/(\Omega/2)\). |
| `metadata.periods`, `metadata.samples_per_half`, `metadata.discard_periods` | Full propagation/readout convention. |
| `projection.target_pair` | Floquet-basis indices of the selected target \(\pi\)-pair for that finite system. |
| `projection.resonance_ranked_external` | External Floquet indices sorted by the stated resonance-weighted local spectral measure. |
| `full_d20` | Full-model continuous TLS phasor at the listed detunings after a 20-period discard. |
| `rows[].K` | Dimension of the target-pair-plus-external-channel Floquet manifold. |
| `rows[].indices` | Exact closed-chain Floquet basis indices retained in that projected manifold. |
| `rows[].effective_d20` | Projected-model continuous TLS phasor on the same detuning grid. |
| `rows[].epsilon_spec` | Euclidean mismatch between independently \(\ell_2\)-normalized full and projected spectra. |

The values are protocol-specific finite-system controls. They are not evidence for a thermodynamic phase boundary, a universal effective theory, or a size-independent minimum retained dimension.

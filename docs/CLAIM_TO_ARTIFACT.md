# Claim-to-artifact map for the submission manuscript

This document maps each manuscript-facing statement to the versioned protocol, committed data, deterministic figure generator, and limitation that must accompany it. It is intentionally narrower than a research notebook: a claim is not permitted in the manuscript merely because a related calculation exists elsewhere in the repository.

| Manuscript statement | Evidence artifact | Regeneration path | Required limitation |
|---|---|---|---|
| A common-product-state TLS readout has a large finite-system OBC/PBC contrast for the held-out $(1,1)$ drive. | `results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/heldout_PBC_m0.json` together with the held-out OBC v2 baseline and the v3 manifest. | `python scripts/gate_a_v3/20_audit_gate_a_v3.py --check-only`; figure via `python scripts/run_submission_checks.py`. | This is an exact finite $N=6$, finite-time protocol observation, not a thermodynamic boundary law or a dissipative invariant. |
| The specified OBC production drive has a reflection-symmetric edge-to-interior response profile. | `production_spatial_m1.json` through `production_spatial_m5.json`, plus the v2 $m=0$ production baseline. | `scripts/gate_a_v3/20_audit_gate_a_v3.py`; `tests/test_result_validation.py`. | The six-site profile is not an asymptotic localization-length measurement. |
| Matched control pairs display drive-class-dependent full-model spectra. | `nu01_OBC_m0.json`, `nu10_OBC_m0.json`, `nu00_OBC_m0.json`, frozen protocol and audit JSON. | `scripts/gate_a_v3/20_audit_gate_a_v3.py --check-only`. | The two pairs are separately period-matched; the sampled four-class data do not support a universal $\nu_\pi$-determined normalized lineshape. |
| The primary late-time response is stable to sampling and to the $20T$/$40T$ discard comparison. | `convergence_s2_d20.json`, `convergence_s8_d20.json`, `convergence_s4_d40.json`. | `scripts/gate_a_v3/20_audit_gate_a_v3.py --check-only`. | The deliberately early $8T$ discard changes detailed lineshape and must be reported as a transient sensitivity. |
| The accepted $g/J=0.06$--$0.12$ points show approximately coupling-linear response-doublet splitting. | `data/checkpoints/floquet_tls_N6_g_frequency_checkpoint.npz` and `results/reproduced/B_geff_scaling_results.json`. | `python scripts/submission/40_generate_coupling_figure.py --check-only`; main coupling panel and supplemental phase panel via normal mode. | At fixed contact and harmonic, $g|B_{0\pi}|$ is a constant rescaling of bare $g$. The four-point fit and its formal errors do not establish an absolute projected matrix element, an experimental uncertainty or an all-coupling perturbative law. |
| The fixed-$N=6$ damping scan exhibits strongest loading at intermediate loss followed by recovery at rapid TLS relaxation. | `data/checkpoints/floquet_tls_N6_gamma_checkpoint.npz`. | `python scripts/submission/20_generate_damping_figure.py --check-only`; figure via `python scripts/run_submission_checks.py`. | This is a deterministic finite-system crossover versus $\gamma_1T$. Fast-defect elimination or Zeno-like decoupling is an interpretation, not a fitted transition or phase boundary. |
| A selected N=4 exact channel pair is quantitatively compatible with an independently fitted late-time stroboscopic trace. | `results/reproduced/C_N4_channel_time_validation_results.json`. | `python scripts/submission/10_generate_mechanism_figures.py --check-only`; figure via `scripts/run_submission_checks.py`. | This is a prepared-mechanism N=4 benchmark, not a single-mode proof or a general N=6 common-preparation effective theory. |
| The N=6 channel checkpoint contains edge-visible near-$-1$ structures. | `data/checkpoints/floquet_tls_N6_edge_seeded_pi_arnoldi_v2_checkpoint.npz`. | Inspect the committed residual-qualified targeted records and the Supplementary Material provenance table. | These are edge-seeded conjugate Ritz pairs, not an exhaustive N=6 channel spectrum or a channel/time lifetime-equality test. |
| The formal $K=2,4,6,8$ controls delimit one tested multichannel validity window and a strong-coupling counterexample. | `data/prb_controls/N6_g0p08_matched_k_convergence.json`, `N8_g0p08_matched_k_convergence.json`, and `N8_g0p12_strong_coupling_k_convergence.json`. | `python scripts/41_plot_prb_controls.py`; first-principles route via `scripts/40_formal_k_convergence.py`. | These calculations use a Floquet-pair-prepared projected state rather than the common-product Gate A contract. They are diagnostics of one reduction, not a second positive size-scaling claim. |
| Low-dimensional Floquet reductions have a preparation-dependent limit. | Gate B2/C1 records and `docs/gate_a_v2/GATE_B_C_ROUTE_DECISION.md`. | Review the cited route-decision document and the associated audit scripts. | Do not claim a generally controlled K-state or finite-harmonic reduction for arbitrary physical preparations. |
| The response-blind N=4 D1 sample obeys its literal stratified raw-weight candidate-screen ordering. | `results/gate_d1/gate_d1.0__6d3a08047527/GATE_D1_N4_WEIGHT_AUDIT.json`, the D1 protocol and corrected route decision. | `python scripts/gate_a_v3/32_audit_gate_d1_n4_weight_screen.py`; inspect the corrected audit hash. | This is an N=4, cross-period, stratified candidate screen. It is neither a common-period causal comparison nor size-persistent N=6 evidence. |
| The \(\nu_\pi\)-associated raw-weight hierarchy persists from N=4 to N=6 for the same eight fixed drives. | `results/gate_d2/gate_d2.0__e615217fa606/MANIFEST.json`, `docs/gate_a_v3/GATE_D2_RESULT_DECISION.md`, and the frozen protocol. | `python scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py --check-only`; eight-drive manuscript figure via `python scripts/submission/30_generate_d2_transfer_figure.py`. | This is a finite, response-blind, cross-period, eight-drive stratified transfer result. It is not a common-period causal law, thermodynamic invariant, universal \(\pi\)-edge spectroscopy or universal normalized lineshape. |

## Release verification

The command below validates all machine-readable artifacts listed above without launching an expensive production run or modifying the committed numerical results:

```bash
python scripts/run_submission_checks.py --check-only
```

The normal mode writes only derived figures and a self-contained hash manifest below `build/submission_checks/`:

```bash
python scripts/run_submission_checks.py --output-dir build/submission_checks
```

The manuscript should cite the exact Git release and Zenodo archive that contain the protocol and result hashes used for the submitted figures.

# Claim-to-artifact map for the submission manuscript

This document maps each manuscript-facing statement to the versioned protocol, committed data, deterministic figure generator, and limitation that must accompany it. It is intentionally narrower than a research notebook: a claim is not permitted in the manuscript merely because a related calculation exists elsewhere in the repository.

| Manuscript statement | Evidence artifact | Regeneration path | Required limitation |
|---|---|---|---|
| A common-product-state TLS readout has a large finite-system OBC/PBC contrast for the held-out $(1,1)$ drive. | `results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/heldout_PBC_m0.json` together with the held-out OBC v2 baseline and the v3 manifest. | `python scripts/gate_a_v3/20_audit_gate_a_v3.py --check-only`; figure via `python scripts/run_submission_checks.py`. | This is an exact finite $N=6$, finite-time protocol observation, not a thermodynamic boundary law or a dissipative invariant. |
| The specified OBC production drive has a reflection-symmetric edge-to-interior response profile. | `production_spatial_m1.json` through `production_spatial_m5.json`, plus the v2 $m=0$ production baseline. | `scripts/gate_a_v3/20_audit_gate_a_v3.py`; `tests/test_result_validation.py`. | The six-site profile is not an asymptotic localization-length measurement. |
| Matched control pairs display drive-class-dependent full-model spectra. | `nu01_OBC_m0.json`, `nu10_OBC_m0.json`, `nu00_OBC_m0.json`, frozen protocol and audit JSON. | `scripts/gate_a_v3/20_audit_gate_a_v3.py --check-only`. | The two pairs are separately period-matched; the sampled four-class data do not support a universal $\nu_\pi$-determined normalized lineshape. |
| The primary late-time response is stable to sampling and to the $20T$/$40T$ discard comparison. | `convergence_s2_d20.json`, `convergence_s8_d20.json`, `convergence_s4_d40.json`. | `scripts/gate_a_v3/20_audit_gate_a_v3.py --check-only`. | The deliberately early $8T$ discard changes detailed lineshape and must be reported as a transient sensitivity. |
| A selected N=4 exact channel pair is quantitatively compatible with an independently fitted late-time stroboscopic trace. | `results/reproduced/C_N4_channel_time_validation_results.json`. | `python scripts/submission/10_generate_mechanism_figures.py --check-only`; figure via `scripts/run_submission_checks.py`. | This is a prepared-mechanism N=4 benchmark, not a single-mode proof or a general N=6 common-preparation effective theory. |
| Low-dimensional Floquet reductions have a preparation-dependent limit. | Gate B2/C1 records and `docs/gate_a_v2/GATE_B_C_ROUTE_DECISION.md`. | Review the cited route-decision document and the associated audit scripts. | Do not claim a generally controlled K-state or finite-harmonic reduction for arbitrary physical preparations. |
| The response-blind N=4 D1 sample obeys its literal stratified raw-weight candidate-screen ordering. | `results/gate_d1/gate_d1.0__6d3a08047527/GATE_D1_N4_WEIGHT_AUDIT.json`, the D1 protocol and corrected route decision. | `python scripts/gate_a_v3/32_audit_gate_d1_n4_weight_screen.py`; inspect the corrected audit hash. | This is an N=4, cross-period, stratified candidate screen. It is neither a common-period causal comparison nor size-persistent N=6 evidence. |
| Gate D2 will test the same eight fixed drives at N=6. | `protocols/gate_d2/gate_d2_n6_nupi_weight_transfer_protocol.json`, runner, validator and local-run instructions. | Before any calculation: `python scripts/gate_a_v3/33_run_gate_d2_n6_weight_transfer.py --dry-run`. | **No Gate D2 N=6 result exists in the source-freeze release.** Do not place a D2 pass/fail or a size-persistent hierarchy statement in the manuscript before the final manifest and audit exist. |

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

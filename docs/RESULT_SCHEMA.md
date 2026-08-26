# Gate A v3 result schema and validation rules

## Scope

The primary common-preparation full-model records use schema `gate_a_v3_full_model_result_v1`. They are JSON files stored beneath `results/gate_a_v3/<protocol-version>__<protocol-hash-prefix>/`. The immutable source records are validated by their manifest hashes and by the record-level self hash. Derived audit files are regenerated into `build/` and are not evidence records.

## Required record fields

| Field | Type | Validation rule | Meaning |
|---|---|---|---|
| `schema` | string | Must equal `gate_a_v3_full_model_result_v1` | Versioned record contract |
| `task` | object | Must match the frozen task when a task is expected | Boundary condition, contact, drive, couplings, periods and readout choices |
| `ratios` | numeric vector | Finite, length at least two, strictly increasing | Dimensionless detuning grid $\omega_d/(\Omega/2)$ |
| `raw_A_TLS` | numeric vector | Finite, non-negative and same length as `ratios` | Modulus of the declared TLS subharmonic phasor |
| `normalized_shape` | numeric vector | Must equal `raw_A_TLS / \|raw_A_TLS\|_2` within floating-point tolerance | Shape-only response representation |
| `W_r` | number | Must equal `trapz(raw_A_TLS**2, ratios)` within tolerance | Ratio-grid integrated spectral weight |
| `preparation` | object | Must declare the common product preparation and absence of Floquet-pair selection | Prevents accidental mixing with prepared-pair diagnostics |
| `provenance` | object | Must contain protocol/script hashes, Git commit and command | Reproducibility path |
| `result_sha256_excluding_self` | string | Must equal SHA-256 of canonical JSON after removing this field | Content-integrity check |

## Cross-record comparisons

A directional ratio, normalized-shape distance or shared-grid integral may only be computed after validating that the compared spectra have exactly the same detuning grid. This requirement is now enforced by `scripts/gate_a_v3/result_validation.py`. It prevents a silent comparison between records that differ in length, spacing, order or unit convention.

The committed v2 baselines use the equivalent field name `detuning_ratios_omega_d_over_Omega_over_2` and are only used as explicitly declared inputs to the Gate A v3 audit. V2 baselines must not be rewritten in the v3 schema merely for convenience, because their original hashes and source provenance are part of the historical evidence chain.

## Gate D2 N=6 result contract

Gate D2 records use schema `gate_d2_n6_full_model_result_v1` and are stored beneath `results/gate_d2/gate_d2.0__e615217fa606/`. The completed campaign contains exactly the eight response-blind-selected drives and `MANIFEST.json`; the original source-freeze remains separately identifiable by its public commit. Every completed record satisfies the following additional rules.

| Requirement | Validation rule |
|---|---|
| Frozen task identity | `task` must be field-by-field identical to one of the eight D1/D2 fixed tasks, after the runner has verified the anchored D1 protocol and corrected-audit hashes. |
| Physical and timing data | The record must state N=6 OBC, contact zero, common product preparation, frozen couplings/readout grid, and timing values consistent with the selected drive. |
| Spectrum and weight | The eleven-point `ratios`, `raw_A_TLS`, normalized shape and recomputed `W_r` must be finite and mutually consistent. |
| Full provenance | Protocol, runner and full-model-helper hashes; public freeze commit; command; UTC bounds; Python/package/platform metadata; threading information; and NumPy BLAS/LAPACK report are required. |
| Resume integrity | The canonical self hash, schema, task, protocol, runner, helper and public-freeze commit must all validate before a completed task may be skipped. |

The final Gate D2 audit verifies the corrected D1 evidence hash, D1 protocol hash, exact N=4/N=6 ratio-grid equality, normalized-shape definition, recomputed weights, runner/helper hashes and the eight-drive final manifest. Its derived JSON and figure output belongs under `build/gate_d2_audit/`, not in the immutable campaign directory. The frozen pass requires both fixed-\(\nu_0\) median ratios above ten and all sampled \(\nu_\pi=1\) weights above all sampled \(\nu_\pi=0\) weights; see `GATE_D2_RESULT_DECISION.md` for the computed values and limitations.

## Validation commands

```bash
python -m pytest -q
python scripts/gate_a_v3/20_audit_gate_a_v3.py --check-only
python scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py --check-only
python scripts/run_submission_checks.py --check-only
```

The first command includes negative tests for self-hash corruption and mismatched ratio grids. The second validates the committed v3 manifest, v3 records and v2/v3 comparisons without writing output. The Gate D2 audit validates the completed eight-result manifest without propagating any physical point. The final command combines tests and all available no-write audit routes for continuous integration or release verification.

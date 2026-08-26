# Gate D1 correction and Gate D2 source-freeze preparation

## Corrected Gate D1 rule

The unchanged frozen Gate D1 protocol states two distinct thresholds:

1. each fixed-$\nu_0$ class-median ratio must exceed 10; and
2. the smallest sampled $\nu_\pi=1$ weight must exceed the largest sampled $\nu_\pi=0$ weight.

The superseded v1 audit incorrectly imposed a factor-10 threshold on both conditions. The unchanged data give 239.10, 4276.67, and 7.004, so the literal frozen rule passes. No response record, selected drive, protocol, or D1 manifest was changed. The corrected machine-readable audit has SHA-256 `34961d819b8dd4cf1f1aaec519161e3d0a2674a5a043e660ad05d00770357f3a`.

## Gate D2 source

The new source-freeze set comprises:

- `protocols/gate_d2/gate_d2_n6_nupi_weight_transfer_protocol.json`
- `scripts/gate_a_v3/gate_d2_validation.py`
- `scripts/gate_a_v3/33_run_gate_d2_n6_weight_transfer.py`
- `scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py`
- `tests/test_gate_d2_freeze.py`
- the corrected Gate D1 audit and route-decision files

The unchanged Gate D2 protocol SHA-256 is:

```text
e615217fa6063ff9c2d400cb927f9d1963d4a29386047fa3c6ae1c40335cd72e
```

## Added protections

Before the first propagation, the runner now:

- verifies the frozen D1 protocol and corrected D1 audit hashes;
- compares every field of all eight D1 and D2 `selected_drives` records;
- requires the corrected D1 audit to report the literal screen as passed;
- requires a clean worktree and verifies that the exact running commit exists on `origin`;
- records runner/helper hashes, Python and package versions, platform, thread settings, and NumPy's BLAS/LAPACK report.

Every completed drive is written atomically and schema-validated before a checkpoint manifest is refreshed. Resume skips only records whose task, protocol, runner, helper, array schema, normalized-shape definition, integrated weight, environment metadata, and self hash all validate.

The final audit supports `--check-only` and writes derived files to `build/gate_d2_audit` by default. It verifies the runner/helper hashes, both evidence anchors, exact N4/N6 grids, finite arrays, normalized-shape definition, raw-weight recomputation, and the eight-drive manifest.

## Scope

No Gate D2 N=6 response belongs in the source-freeze commit. A successful later Gate D2 result may support only a sampled, finite-size-persistent, stratified-protocol raw-weight hierarchy. It cannot establish a common-period causal law, a thermodynamic invariant, universal $\pi$-edge spectroscopy, or a universal lineshape.

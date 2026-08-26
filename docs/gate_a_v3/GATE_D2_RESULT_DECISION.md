# Gate D2 N=6 finite-size transfer: completed-result decision

## Frozen route and completed campaign

Gate D2 was executed only after the public source-freeze commit `216b0791c224da446fc6530224c3dfc2cff54f19` was available on `main`. The source protocol is [`gate_d2_n6_nupi_weight_transfer_protocol.json`](../../protocols/gate_d2/gate_d2_n6_nupi_weight_transfer_protocol.json), whose SHA-256 is `e615217fa6063ff9c2d400cb927f9d1963d4a29386047fa3c6ae1c40335cd72e`. The runner verified both the D1 protocol anchor and corrected D1 audit anchor, then propagated the eight preselected N=6 tasks without adding, replacing, or retuning a drive.

The final raw-result manifest is [`MANIFEST.json`](../../results/gate_d2/gate_d2.0__e615217fa606/MANIFEST.json). Its complete campaign integrity is checked by:

```bash
python scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py --check-only
```

The check validates all eight result-file hashes, result self-hashes, schema, field-by-field task identity, N=4/N=6 ratio-grid identity, normalized-shape definitions, recomputed integrated weights, and runner/helper hashes.

## Frozen decision

| Frozen quantity | N=6 completed value | Criterion | Status |
|---|---:|---:|---|
| Fixed-\(\nu_0=0\) median ratio \(\mathrm{median}(W_{\nu_{01}})/\mathrm{median}(W_{\nu_{00}})\) | 409.536 | \(>10\) | Pass |
| Fixed-\(\nu_0=1\) median ratio \(\mathrm{median}(W_{\nu_{11}})/\mathrm{median}(W_{\nu_{10}})\) | 5633.720 | \(>10\) | Pass |
| All-point ordering \(\min W_{\nu_\pi=1}/\max W_{\nu_\pi=0}\) | 12.048 | \(>1\) | Pass |
| Frozen Gate D2 decision | — | Both conditions pass | **Pass** |

The secondary, descriptive N=4-to-N=6 log-weight Pearson correlation is `0.999514`, and the median N=6/N=4 weight ratio is `0.918114`. These quantities are useful descriptive size-transfer diagnostics; they are not additional predeclared success criteria.

## Permitted manuscript statement

> In the same response-blind, cross-period, eight-drive stratified protocol, the \(\nu_\pi\)-associated raw-weight hierarchy that passed the N=4 screen also passes the frozen N=6 transfer test.

The statement must be accompanied by the protocol, both frozen conditions, the result manifest, and the following limitations.

## Prohibited inference

The completed Gate D2 pass does **not** establish a common-period causal law, a thermodynamic topological invariant, universal \(\pi\)-edge spectroscopy, a universal normalized lineshape, or a phase boundary. It is a finite, protocol-specific persistence result for the same eight response-blind-selected drives.

No additional drive, N=8/N=10 extension, or response-informed sweep is authorized under Gate D2. The complete result directory and this decision record should be released together as a post-freeze data commit.

## Derived figure

The audit regenerates a deterministic N=4-versus-N=6 raw-weight transfer scatter into an ignored build directory:

```bash
python scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py \
  --output-dir build/gate_d2_audit
```

The generated `GATE_D2_N4_N6_WEIGHT_TRANSFER.png` is a compact evidence figure; retain the associated derived audit JSON and manifest hash with the manuscript submission package.

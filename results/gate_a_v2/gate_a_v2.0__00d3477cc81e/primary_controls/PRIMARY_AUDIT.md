# Gate A v2 primary-control audit

**Frozen protocol SHA-256:** `00d3477cc81e29ddbd6f794365b4e360604b78b70604a529a908d77612c4bbcf`  
**Manifest SHA-256:** `ec12c22ec5fce7f5499a9df035f2ffd6e754c363f69421369191b002550d4cb9`

> This is a finite N=6 audit under a common product-state preparation. It is not a thermodynamic-limit or phase-boundary claim.

| Control | W_top/W_control at m=0 | D(shape) | R_EB(top)/R_EB(control) | Directional decision |
|---|---:|---:|---:|---|
| topological_pbc_same_drive_v2 | 1602 | 0.5625 | 981.5 | pass |
| trivial_obc_control_v2 | 6973 | 1.005 | 978.8 | pass |

**Frozen symmetric-rule decision:** `pass_to_heldout`.
**Conservative directional interpretation:** `pass_to_heldout`.

The protocol's symmetric C_W definition and the requested directional W ratio are both retained; the latter is not inserted retroactively into the frozen decision rule. No held-out run is authorized unless the conservative directional interpretation is `pass_to_heldout`.

## Integrity

All six source files match the SHA-256 values in `MANIFEST.json`. Every source record declares `floquet_pair_selected_for_full_model=false` and `B0_constructed_for_full_model=false`.

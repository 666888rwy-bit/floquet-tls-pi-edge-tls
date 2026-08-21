# Gate A v2: initial-state and spatial-diagnostic feasibility audit

## Purpose

This audit is completed **before any Gate A v2 full-spectrum propagation**. It checks that the finalized protocol `protocols/gate_a_v2/gate_a_v2_protocol.json` can be implemented at finite \(N=6\) without using a selected Floquet pair, a Schur-output index, \(B^{(0)}\), or the phase of \(\langle\phi_a|Z_m|\phi_b\rangle\) to define the full-model state.

> **Scope.** This is an implementation-feasibility record, not a result. It does not establish a boundary signature, a topological phase boundary, or any thermodynamic-limit conclusion.

## Common physical preparation

The chain state is the computational-basis product state

\[
\rho_{\rm ch}(0)=\bigl(|\uparrow_z\rangle\langle\uparrow_z|\bigr)^{\otimes 6},
\qquad
\rho_d(0)=|0_d\rangle\langle0_d|,
\]

where \(|0_d\rangle\) is the \(Z_d=+1\) TLS basis state used by the existing production implementation. In the code this state is created directly as one computational-basis vector of the **full chain–TLS Hilbert space**, then converted to a density matrix. Its definition has no dependence on the drive, boundary condition, local Floquet matrix element, or diagonalization convention.

| Audit question | Implementation decision | Consequence |
|---|---|---|
| Does the full model need a selected \(0\)-\(\pi\) pair? | No. The initial state is built before any Floquet diagonalization. | A trivial or PBC control cannot be blocked merely because a pair is absent, degenerate, or has a zero \(Z_m\) matrix element. |
| Does the full model need \(\arg\langle\phi_a|Z_m|\phi_b\rangle\)? | No. This quantity is not evaluated in the Gate A full-response path. | The preparation has no hidden phase injection tied to a near-\(\pi\) energy difference. |
| Is a common initial state maintained across control drives? | Yes. The same full-system computational-basis vector is used for all four drive labels. | Differences can be attributed only to the declared boundary, drive, contact site, and matched detuning variables. |

## Fixed spatial comparison

Each primary drive/boundary case is evaluated with the TLS exchange contact at \(m=0\) and \(m=3\). The first is the fixed left-edge contact in OBC. The second is the fixed interior reference for \(N=6\). For PBC, these remain fixed numerical locations, not claims of a physical edge and bulk.

The comparison uses the fixed ratio-grid spectral weight

\[
W_r=\int_{0.88}^{1.12}|A_{\rm TLS}(r)|^2\,dr,
\qquad r=\omega_d/(\Omega/2),
\]

and the finite-size spatial diagnostic

\[
R_{\rm EB}=\frac{W_r(m=0)}{\max[W_r(m=3),10^{-15}]}.
\]

This diagnostic is well-defined whenever the phasor outputs are finite. The \(10^{-15}\) floor is solely a numerical guard in a ratio; it is not an imputed physical signal. The protocol requires raw spectra to be retained, so a vanishing denominator remains visibly auditable.

| Diagnostic | What it can support at \(N=6\) | What it cannot support |
|---|---|---|
| \(R_{\rm EB}\) under a common preparation | A fixed finite-system edge-contact versus interior-reference contrast | A localization length, a sharp boundary transition, or a thermodynamic edge-mode proof |
| Topological OBC / same-drive PBC contrast | A finite-size boundary-condition sensitivity under matched drive and preparation | A statement that PBC lacks all near-\(\pi\) many-body energy differences |
| Topological OBC / trivial OBC contrast | A finite-size drive-class sensitivity selected by the closed-chain classifier | A claim that every trivial drive has no TLS response |

## Computational feasibility

At \(N=6\) the full chain plus TLS Hilbert-space dimension is \(2^7=128\), and the vectorized density-matrix evolution dimension is \(128^2=16\,384\). The existing repository's direct N=6 sparse `expm_multiply` check uses the same dimensionality. Gate A v2 needs 3 primary cases \(\times\) 2 contacts \(\times\) 11 detunings, for 66 exact response traces. The held-out drive is deliberately excluded until the frozen three-control decision rule is evaluated.

The production script will build the product state once per case/contact and then use the same sparse piecewise Floquet–Lindblad propagator, time grid, damping channel, phasor definition, and discarded transient convention as the previously audited N=6 reference. The only intentional differences are the **pair-independent preparation** and the addition of the fixed \(m=3\) reference contact.

## Audit decision

The common preparation and spatial diagnostics are computationally feasible and scientifically defined under the finalized v2 protocol. The next permitted step is to implement the full-model script and provenance layer, commit them publicly, and only then execute the 66-trace primary control calculation.

## References

[1]: ../../protocols/gate_a_v2/gate_a_v2_protocol.json "Gate A v2.0 finalized protocol; common initial state, frozen control set, diagnostics, decision rule, and provenance requirements."

[2]: ../REPRODUCIBILITY.md "Project reproducibility protocol, including the finite-size scope statement and the existing direct N=6 implementation check."

# Gate C1 audit: micromotion/Fourier feasibility at N=4

**Decision: Gate C1 fails its prospective criterion for scaling the reduced model to N=6.** Retaining the \(n=\pm1\) Fourier harmonics accurately reconstructs the exact micromotion *within the declared K=8 Floquet subspace*, but that entire K=8 reduced subspace remains quantitatively inconsistent with the exact N=4 chain–TLS response. The dominant obstruction is therefore not the discarded Fourier harmonics of \(B(t)\).

## Frozen setup and provenance

The public protocol is [`gate_c1_micromotion_feasibility_protocol.json`](../../../protocols/gate_a_v2/gate_c1_micromotion_feasibility_protocol.json), with SHA-256 `35d0aebc691bf940a995a8d1c42d5e939327da03f50b710c198fa8b558b60`. The machine-readable calculation is [`GATE_C1_MICROMOTION_FEASIBILITY.json`](GATE_C1_MICROMOTION_FEASIBILITY.json), run at public commit `bb42f5b`.

The frozen test used the N=4 OBC production drive \((\alpha,\beta)=(0.75\pi,0.90\pi)\), \(g=\gamma_1=0.08\), a TLS at \(m=0\), and the same 11 detunings, 80 periods, four samples per half step and 20-period discard as the prior full-model protocol. The full chain–TLS model begins in \(|\uparrow_z\rangle^{\otimes4}\otimes|0_d\rangle\). No Floquet pair is used to prepare the full model.

The declared hybrid rule selected K=8, with \(p_8=0.93984\). The selected local near-\(\pi\) pair is only an anchor for the reduced basis; its numerical indices are not physical labels.

## Result

| Model | \(\epsilon_{\rm spec}\) vs exact N=4 full model | Raw peak ratio vs full | Key comparison |
|---|---:|---:|---|
| Static \(B^{(0)}\) | 0.4115 | 1.2154 | Baseline static reduction |
| Fourier \(M=1\) | 0.4841 | 3.2250 | \(\epsilon_{M1,\mathrm{micro}}=0.00159\) |
| Fourier \(M=2\) | 0.4841 | 3.2253 | \(\epsilon_{M2,\mathrm{micro}}=0.00157\) |
| Exact \(B(t)\) within K=8 | 0.4835 | 3.2451 | Within-subspace micromotion reference |

The \(M=1\) Fourier reconstruction agrees with exact within-K micromotion at the level \(1.59\times10^{-3}\) in normalized spectral shape, and adding \(M=2\) changes that number negligibly. Thus the protocol's Fourier-harmonic convergence test **passes**. But \(M=1\) fails the actual full-model targets: its shape error is 0.4841 (target \(\le0.35\)), it is not an improvement over static \(B^{(0)}\), and its raw peak is larger than the full-model peak by a factor 3.225 (allowed range 0.50–2.00).

> **Error attribution.** At this N=4 production test, the large discrepancy is already present after micromotion is treated essentially exactly *inside the retained K=8 manifold*. The failure cannot therefore be repaired merely by appending \(n=\pm1\) or \(n=\pm2\) Floquet/Sambe harmonics to the present local manifold. The issue is consistent with the finite state-space reduction itself and/or the projection of the dissipative full-model dynamics, not with zero-harmonic truncation alone.

## Consequence for the manuscript route

Do not execute an N=6 Fourier/Sambe extension of the current K-state model, and do not claim that its static \(B^{(0)}\)-only formulation is the controlled source of the observed full-model TLS spectra. The defensible result is narrower but valuable: Gate A v2 provides an exact finite-system, common-preparation OBC/PBC/trivial control; Gate B and Gate C show precisely why the existing local reduced model is preparation-conditional and quantitatively incomplete.

The highest-value next step is not a larger calculation. It is a conceptual restructuring of the PRB narrative: present the exact full-chain–TLS finite-system topology controls as the principal result, retain the pair/channel model only as a deliberately prepared coherence mechanism, and disclose the common-preparation limitation. A new general effective theory would require a different projection formalism that includes occupied sectors and their dissipative coupling, not merely more Fourier replicas.

## References

[1]: ../../../protocols/gate_a_v2/gate_c1_micromotion_feasibility_protocol.json "Gate C1.0 prospectively frozen micromotion feasibility protocol."

[2]: GATE_C1_MICROMOTION_FEASIBILITY.json "Machine-readable N=4 Fourier/micromotion feasibility calculation."

[3]: ../gate_b2/GATE_B2_AUDIT.md "Gate B2 initial-support manifold audit."

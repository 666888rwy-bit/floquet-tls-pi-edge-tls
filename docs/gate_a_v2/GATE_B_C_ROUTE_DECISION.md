# Gate B–C route decision after the common-preparation controls

## Executive decision

The project now has a clear division between a **successful finite-system full-model result** and an **unsuccessful general reduced-model claim**. The exact Gate A v2 OBC/PBC/trivial controls are scientifically usable, within their stated finite-\(N=6\) scope. The present local Floquet pair/manifold reduction is not a quantitatively controlled description of TLS spectroscopy from the common physical product preparation, even after an initial-support-aware extension and a micromotion/Fourier-harmonic test.

> **Stop rule.** Do not scale the current reduced model to N=6, N=8, or N=10. Do not spend computation on additional Fourier replicas of this K-state construction. The N=4 Gate C1 test already isolates the issue: the M=1 Fourier model agrees with the exact within-K micromotion model, but both fail against the exact full chain–TLS response.

## Evidence chain

| Gate | Question | Outcome | Manuscript consequence |
|---|---|---|---|
| Gate A v2 | Does a common physical preparation yield finite-system OBC/PBC/trivial discrimination without pair preparation? | **Pass.** Large edge spectral-weight and edge/interior contrasts at the declared \((\nu_0,\nu_\pi)=(1,1)\) drive; held-out OBC point retains an edge/interior contrast. | This is the principal exact numerical result. Use carefully scoped finite-system language. |
| Gate B1 | Why does the original K=2/K=4 local pair model fail for the common preparation? | The physical initial state is distributed over roughly 11–16 Floquet states for 90–95% coverage. | Pair-only preparation is not representative of a natural product state. |
| Gate B2 | Does an initial-support-compatible hybrid K manifold repair the reduced model? | **Fail at frozen K=16 rule.** \(p_{16}>0.94\), but spectral-shape error remains 0.429 (production) and 0.381 (held-out). | Do not state that K=4 or K=16 is a generally controlled local spectroscopy manifold. |
| Gate C1 | Is the remaining failure due to discarding nonzero Floquet harmonics? | **No.** M=1 matches exact within-K micromotion to \(1.6\times10^{-3}\), while both differ substantially from full N=4 dynamics. | More Sambe replicas alone are not the remedy; do not run an N=6 Fourier extension. |

## Manuscript route

The strongest defensible paper is now an exact finite-system study of **common-preparation TLS edge sensitivity**, with the reduced model repositioned as a deliberately prepared coherence mechanism rather than the source of a universal quantitative prediction. The title, abstract and conclusion should not claim a generally valid minimal local Floquet manifold.

The paper may state that, for the specified finite drive and dissipation protocol, the topological OBC case has a markedly larger TLS spectral weight at an edge contact than the same-drive PBC and the declared trivial OBC control, while a held-out topological OBC drive retains a large edge/interior contrast. It must explicitly say that these are finite-system comparisons and that the closed-chain BDI classifier is used only to label the control drives.

The paper should separately disclose the reduced-model limitation: under a common \(|\uparrow_z\rangle^{\otimes N}\) preparation, the physical state is not concentrated in the selected local near-\(\pi\) manifold. Enlarging the manifold to capture initial-state weight does not achieve the frozen shape-error target, and exact within-manifold micromotion does not resolve the discrepancy. This limitation strengthens credibility because it prevents a false reduction claim.

## Recommended next research task

The appropriate next task is editorial and conceptual rather than a brute-force numerical sweep. The PRB manuscript should be restructured around the exact Gate A v2 controls, the invariant map, and a transparent limitations section. If a new general effective theory is desired later, it needs a different projection that treats the physically occupied Floquet sectors and dissipative coupling together; it should begin with an independently derived Nakajima–Zwanzig/Feshbach or Liouvillian projection scheme at N=4, not with a larger K or harmonic cutoff.

## Public audit trail

The public repository contains the frozen protocols, executable scripts, raw JSON outputs and machine-readable SHA-256 provenance. Key result commits are [`dc69d6e`](https://github.com/666888rwy-bit/floquet-tls-pi-edge-tls/commit/dc69d6e) for Gate A v2's final audit, [`633124a`](https://github.com/666888rwy-bit/floquet-tls-pi-edge-tls/commit/633124a) for Gate B2 results, and [`f3f7575`](https://github.com/666888rwy-bit/floquet-tls-pi-edge-tls/commit/f3f7575) for Gate C1 results.

## References

[1]: ../results/gate_a_v2/gate_a_v2.0__00d3477cc81e/GATE_A_V2_FINAL_AUDIT.md "Gate A v2 final finite-system full-model audit."

[2]: ../results/gate_a_v2/gate_a_v2.0__00d3477cc81e/gate_b2/GATE_B2_AUDIT.md "Gate B2 initial-support manifold audit."

[3]: ../results/gate_a_v2/gate_a_v2.0__00d3477cc81e/gate_c1/GATE_C1_AUDIT.md "Gate C1 micromotion/Fourier feasibility audit."

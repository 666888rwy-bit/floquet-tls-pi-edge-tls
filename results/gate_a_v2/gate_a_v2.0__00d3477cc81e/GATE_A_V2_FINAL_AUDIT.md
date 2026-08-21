# Gate A v2 final audit: common-preparation finite-system controls

**Status: completed finite-\(N=6\) control campaign; the full-model Gate A decision passes its prospectively frozen finite-system rule, while Gate B fails as a general-preparation reduced-model test.** This record supersedes the scientific role of the earlier pair-prepared Gate A v1 control. It is deliberately not a thermodynamic-limit, open-system phase-boundary, or universal TLS-spectroscopy claim.

> **Canonical deliverable.** This audit is Markdown plus immutable JSON, SHA-256 manifests, source scripts and deterministic PNG/PDF figures. No DOCX is a deliverable in this version.

## 1. Public provenance and protocol integrity

The full-model preparation, controls, metrics, thresholds and run-provenance rules were frozen in the public repository before any v2 full spectra were launched. The protocol is available at [`protocols/gate_a_v2/gate_a_v2_protocol.json`](../../../protocols/gate_a_v2/gate_a_v2_protocol.json), with SHA-256

```text
00d3477cc81e29ddbd6f794365b4e360604b78b70604a529a908d77612c4bbcf
```

The implementation and protocol first appeared in public commit [`11a6863`](https://github.com/666888rwy-bit/floquet-tls-pi-edge-tls/commit/11a6863), while the exact primary-control propagations record public code commit [`15e1f98`](https://github.com/666888rwy-bit/floquet-tls-pi-edge-tls/commit/15e1f98). The held-out calculation records commit [`ec51f61`](https://github.com/666888rwy-bit/floquet-tls-pi-edge-tls/commit/ec51f61). Every source JSON records the protocol and script SHA-256, Git commit, repository URL, exact command, UTC start/finish timestamps, software versions and its self-excluding result hash.

The primary manifest verifies all six primary source-result files; its SHA-256 is `ec12c22ec5fce7f5499a9df035f2ffd6e754c363f69421369191b002550d4cb9`. The held-out manifest independently verifies both held-out source files. All full-model JSON records explicitly state:

```text
floquet_pair_selected_for_full_model = false
B0_constructed_for_full_model = false
```

Thus the full-model topology test did not select a Floquet pair, copy numerical Floquet indices, construct \(B^{(0)}\), or use \(\arg\langle\phi_a|Z_m|\phi_b\rangle\) to define the initial state.

## 2. What was fixed before propagation

Every complete response started from the same physical product state

\[
\rho(0)=\left(|\uparrow_z\rangle\langle\uparrow_z|\right)^{\otimes 6}\otimes |0_d\rangle\langle0_d|.
\]

The primary cases were topological OBC \((\alpha,\beta)=(0.75\pi,0.90\pi)\), same-drive PBC, and invariant-selected trivial OBC \((0.50\pi,0.04\pi)\). All used \(g=\gamma_1=0.08\), the same 11-point ratio grid \(r=\omega_d/(\Omega/2)\), 80 periods, four samples per half step and a 20-period discard. The TLS exchange contact was evaluated at a fixed edge reference \(m=0\) and interior reference \(m=3\). These are finite-system reference locations, not a localization-length measurement.

The primary statistics were fixed as the ratio-grid spectral weight \(W_r=\int |A_{\rm TLS}(r)|^2dr\), shape distance \(D=\|\hat a-\hat b\|_2\), and \(R_{\rm EB}=W_r(m=0)/W_r(m=3)\). The decisive direction is topological OBC divided by the stated control, even though the initially committed implementation also retained a symmetric \(\max(W_t/W_c,W_c/W_t)\) record. Both are reported in the source audit; the directional numbers below are the conservative manuscript-relevant ones.

## 3. Primary full-model control result

| Comparison at \(m=0\) | \(W_{\rm top\,OBC}/W_{\rm control}\) | \(D\) | \(R_{\rm EB}^{\rm top\,OBC}/R_{\rm EB}^{\rm control}\) | Frozen thresholds | Outcome |
|---|---:|---:|---:|---|---|
| Topological OBC / same-drive PBC | 1601.79 | 0.5625 | 981.45 | \(\ge1.50,\;\ge0.30,\;\ge1.50\) | Pass |
| Topological OBC / trivial OBC | 6973.43 | 1.0053 | 978.81 | \(\ge1.50,\;\ge0.30,\;\ge1.50\) | Pass |

The raw topological-OBC spectrum has \(W_r(m=0)=3.32466\times10^{-3}\), while the same-drive PBC and trivial-OBC values are \(2.07559\times10^{-6}\) and \(4.76761\times10^{-7}\), respectively. The topological OBC edge/interior ratio is \(R_{\rm EB}=981.45\); PBC gives exactly unity to numerical precision because the uniform preparation and periodic Hamiltonian make the two fixed contacts equivalent, while the trivial OBC control gives \(R_{\rm EB}=1.00270\).

The diagnostic features are intentionally reported without overinterpretation. On the frozen 11-point grid, the topological OBC edge spectrum satisfies the predeclared resolved-two-maxima rule at \(r=0.928\) and \(1.096\), separated by \(0.168\). The same-drive PBC also has two grid maxima under that mechanical rule, separated by \(0.072\); the trivial OBC control has no resolved splitting and a reportable interpolated FWHM of \(0.0461\) in ratio units. The topological OBC FWHM is censored by the fixed grid, so no linewidth comparison beyond that statement is warranted.

The verified raw spectra are displayed in [`PRIMARY_CONTROLS_RAW_SPECTRA.png`](primary_controls/PRIMARY_CONTROLS_RAW_SPECTRA.png). The corresponding machine-readable audit is [`PRIMARY_AUDIT.json`](primary_controls/PRIMARY_AUDIT.json), and its short human-readable companion is [`PRIMARY_AUDIT.md`](primary_controls/PRIMARY_AUDIT.md).

> **Gate A v2 primary decision.** Under the common physical preparation and the predeclared finite-\(N=6\) metrics, the three-way full-model control passes the rule permitting the single predeclared held-out topological drive. This supports a controlled **finite-system association** between the closed-chain drive classifier, an edge contact and the measured TLS response. It does not establish a phase boundary, a thermodynamic invariant for the dissipative problem, or universal spectroscopy.

## 4. Held-out topological OBC observation

The held-out drive \((\alpha,\beta)=(0.50\pi,0.96\pi)\), classified by the same closed-chain convention as \((\nu_0,\nu_\pi)=(1,1)\), was run only after the primary controls passed. It used no re-tuned full-model parameter or state-preparation choice. Its edge spectral weight is \(W_r(m=0)=2.52608\times10^{-3}\), its interior-reference value is \(1.57182\times10^{-6}\), and its resulting finite-reference ratio is

\[
R_{\rm EB}^{\rm heldout}=1607.11.
\]

The held-out edge spectrum also has a pronounced central minimum at \(r=1\) and flanking maxima on the frozen grid. This confirms that a large edge-versus-interior contrast under the same common preparation is **not confined to the original production point**.

However, this held-out run contains only the predeclared held-out topological OBC drive; it does **not** include a new matching PBC/trivial pair at the held-out parameters. It therefore cannot independently reproduce the complete three-way topological-specificity contrast. It is a held-out persistence check of the edge-contact response, not a second independent phase-control test.

## 5. Gate B: projected local-manifold validity under the common preparation

Gate B was intentionally separated from full-model Gate A. A local near-\(\pi\) pair and its K=4 extension are used only to define a post hoc projector \(P_K\); they never define the full-system initial state. The retained weight is \(p_K=\mathrm{Tr}(P_K\rho_{\rm ch}(0))\).

| Drive and contact | \(p_2\) | \(p_4\) | K=2 result | K=4 result |
|---|---:|---:|---|---|
| Production topological OBC, \(m=0\) | 0.004658 | 0.011159 | \(\epsilon_{\rm spec}=0.8752\), peak ratio \(1.36\times10^{-3}\) | \(\epsilon_{\rm spec}=0.7173\), peak ratio 0.5428 |
| Held-out topological OBC, \(m=0\) | \(8.08\times10^{-30}\) | \(1.65\times10^{-29}\) | Undefined by \(p_K\le10^{-12}\) rule | Undefined by \(p_K\le10^{-12}\) rule |

The earlier pair-prepared convergence result is therefore **not transferable** to the common physical preparation. At the production point, K=4 retains only about 1.12% of the chain initial-state weight and fails to reproduce the normalized full-model shape. At the held-out point, the selected K=2/K=4 manifolds have effectively zero overlap with the physical product state. This is a scientific limitation of the present pair/manifold reduction, not a numerical failure.

> **Gate B decision.** Do not claim that the current K=2/K=4 local Floquet model describes general TLS spectroscopy from a natural common product preparation. It remains a model for deliberately pair-weighted preparations. Any PRB upgrade must either enlarge/redefine the manifold around physically occupied sectors or present the reduction as preparation-conditional.

## 6. Manuscript-safe conclusion and next decision

The scientifically defensible v2 statement is narrow:

> In the specified finite \(N=6\) driven Ising chain with a common product-state preparation, a locally coupled damped TLS exhibits a substantially larger edge-contact spectral weight and edge/interior contrast at the closed-chain \((\nu_0,\nu_\pi)=(1,1)\) production drive than at the same-drive PBC and the declared trivial OBC control. A separated held-out \((1,1)\) OBC drive retains a large edge/interior contrast.

The following statements remain unsupported and must not enter the manuscript: thermodynamic-limit topology, a dissipative phase boundary, universal TLS topological spectroscopy, or a generally valid K=4 pair-plus-channel reduction. The current Gate A v2 supports proceeding with finite-system topological-specificity language only if this scope is stated explicitly; the Gate B result is a mandatory limitation in any stronger PRB framing.

## References

[1]: ../../../protocols/gate_a_v2/gate_a_v2_protocol.json "Gate A v2.0 prospectively frozen numerical protocol."

[2]: primary_controls/PRIMARY_AUDIT.json "Machine-readable primary-control integrity and metric audit."

[3]: heldout_controls/MANIFEST.json "Held-out exact-result manifest with source-file hashes and public code commit."

[4]: https://doi.org/10.1103/PhysRevB.96.045422 "Floquet topological phases in a driven Ising chain, Physical Review B 96, 045422 (2017)."

[5]: https://doi.org/10.1103/PhysRevB.99.205419 "Floquet edge modes in driven spin chains, Physical Review B 99, 205419 (2019)."

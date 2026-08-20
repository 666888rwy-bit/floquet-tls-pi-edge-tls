# PRB multichannel Floquet controls

This document records the formal numerical controls added after the initial reviewer-facing release. They test a precise finite-system statement:

> A single Floquet edge-state pair is insufficient for the stated local dissipative TLS response, while a minimal resonance-weighted local multichannel manifold can be predictive in a controlled coupling window and loses predictivity at stronger coupling.

The calculations are **not** a thermodynamic-limit analysis, a phase-boundary calculation, or a proof that every possible effective theory must fail outside the displayed window.

## 1. Fast reviewer route

The committed JSON summaries contain the full 11-point response spectra, selected subspace indices, protocol metadata, and normalized spectral errors. Regenerate the two audit figures and a human-readable table in seconds:

```bash
python scripts/41_plot_prb_controls.py
```

This writes the following files under `results/reproduced/prb_controls/`:

| File | Contents |
|---|---|
| `PRB_F6_matched_positive_controls.png` | Full-versus-projected spectral overlays at matched N=6 and N=8 positive anchors. |
| `PRB_three_control_K_convergence.png` | The three control curves for \(\epsilon_{\rm spec}(K)\). |
| `PRB_multichannel_controls_audit.md` | Numerical table and the applicable inference boundary. |

The frozen figure references are retained under `results/manuscript_figures/prb_controls/` and are not overwritten by the fast script.

## 2. Formal production protocol

| Convention | Value |
|---|---|
| Drive | Two-step Ising drive with \(J=h=1\), \(\alpha=0.75\pi\), \(\beta=0.90\pi\) |
| Detuning grid | 11 values of \(\omega_d/(\Omega/2)\) from 0.88 to 1.12 |
| Propagation | 80 drive periods; 4 continuous samples per drive half-step |
| Readout | Continuous TLS phasor at \(\Omega/2\), after discarding 20 periods |
| Initial chain state | Equal-coherence state in the selected closed-chain target \(\pi\)-pair, with phase set by the boundary \(Z_0\) matrix element |
| Reduced manifolds | Target pair plus the first \(K-2\) external states under the resonance-weighted local ranking, with \(K=2,4,6,8\) |
| Error metric | Euclidean distance between independently \(\ell_2\)-normalized full and projected response spectra |
| Interpretation thresholds | Predictive: \(\epsilon_{\rm spec}\leq0.20\); intermediate: \(0.20<\epsilon_{\rm spec}\leq0.35\); breakdown: \(\epsilon_{\rm spec}>0.35\) |

The threshold bands are predeclared modeling criteria. They are not thermodynamic phase boundaries.

## 3. Matched cross-size positive controls and N=8 counterexample

| Control | \(K=2\) | \(K=4\) | \(K=6\) | \(K=8\) | Interpretation |
|---|---:|---:|---:|---:|---|
| N=6, \(g=0.08\), \(\gamma_1=0.08\) | 0.3646 | 0.1467 | 0.1442 | 0.1610 | Pair-only is nonpredictive; the minimal \(K=4\) manifold enters the predictive window. The K=8 residual is nonmonotonic but remains predictive. |
| N=8, \(g=0.08\), \(\gamma_1=0.08\) | 0.3466 | 0.1452 | 0.1413 | 0.1384 | A representative larger finite system exhibits the same dominant \(K=2\rightarrow4\) correction. |
| N=8, \(g=0.12\), \(\gamma_1=0.08\) | 0.2950 | 0.6287 | 0.6220 | 0.6133 | Tested resonance-weighted \(K=4\)–8 local manifolds form a high-error plateau. |

The first two rows use an exactly matched protocol. The third row changes only the coupling relative to the N=8 positive anchor and supplies a controlled strong-coupling counterexample. Its conclusion is deliberately limited to the tested local ranking and \(K\leq8\) manifold sizes.

## 4. N=6 model-error anchors

The compact JSON file `data/prb_controls/N6_K4_model_error_anchors.json` records the six N=6 production anchors. For the minimal \(K=4\) locally weighted manifold, the normalized errors are:

| \(\gamma_1\) | \(\epsilon_{\rm spec}(g=0.08)\) | Classification | \(\epsilon_{\rm spec}(g=0.12)\) | Classification |
|---:|---:|---|---:|---|
| 0.04 | 0.2398 | intermediate | 0.6303 | breakdown |
| 0.08 | 0.1386 | predictive | 0.4679 | breakdown |
| 0.16 | 0.0587 | predictive | 0.2459 | intermediate |

This is called a **model-error map** or **validity map**. It should not be interpreted as a phase diagram.

## 5. Full-production route

For a first-principles rerun, use the direct script. It recomputes the closed Floquet basis, local spectral ranking, full Floquet--Lindblad spectra, projected spectra, JSON summary, and a comparison plot:

```bash
# Matched N=6 positive anchor
python scripts/40_formal_k_convergence.py --n 6 --g 0.08

# Matched N=8 positive anchor
python scripts/40_formal_k_convergence.py --n 8 --g 0.08

# N=8 strong-coupling counterexample
python scripts/40_formal_k_convergence.py --n 8 --g 0.12
```

The N=8 commands are intentionally expensive full Liouville-space calculations. They may take tens of minutes and require substantially more RAM than the checkpoint-based scripts. The stored JSON files are provided so that a reviewer can audit all final response values and regenerate the main K-convergence figures without incurring that cost.

## 6. File provenance

| Public file | Provenance | Role |
|---|---|---|
| `data/prb_controls/N6_g0p08_matched_k_convergence.json` | Formal N=6 matched run | Positive anchor data |
| `data/prb_controls/N8_g0p08_matched_k_convergence.json` | Formal N=8 matched run | Cross-size positive control |
| `data/prb_controls/N8_g0p12_strong_coupling_k_convergence.json` | Formal N=8 second-coupling run | Strong-coupling counterexample |
| `data/prb_controls/N6_K4_model_error_anchors.json` | N=6 31-detuning production anchors | Finite-system error-window context |
| `scripts/40_formal_k_convergence.py` | Direct sparse Floquet--Lindblad calculation | High-cost independent recomputation |
| `scripts/41_plot_prb_controls.py` | JSON analysis and plotting | Fast reviewer audit |

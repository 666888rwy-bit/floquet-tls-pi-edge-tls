# Reproducibility protocol

## 1. Scope and current evidence hierarchy

This repository studies a **finite** periodically driven Ising chain locally exchange-coupled to an amplitude-damped TLS. The current primary evidence is Gate A v3: exact N=6 Floquet–Lindblad full-model calculations with a common product preparation, closed-chain BDI-labelled drive controls, and public hash provenance.

> **Scope statement.** The computations establish protocol-specific finite-size, finite-time, and readout-window-dependent results. They do not establish a thermodynamic-limit time-crystal phase, a sharp dissipative phase boundary, a universal TLS effective theory, a unique \(\nu_\pi\)-controlled response, or an asymptotic localization law.

| Evidence tier | Location | Role |
|---|---|---|
| Exact Gate A v3 geometry controls | `protocols/gate_a_v3/`, `scripts/gate_a_v3/`, `results/gate_a_v3/` | Primary common-preparation OBC/PBC and contact-position evidence. |
| Same-period BDI-labelled controls | Same Gate A v3 records and audits | Limits the interpretation: the sampled normalized line shapes are not fixed by \(\nu_\pi\) alone. |
| Gate D1 and Gate D2 | `protocols/gate_d1/`, `protocols/gate_d2/`, `results/gate_d1/`, `results/gate_d2/` | Corrected response-blind N=4 screen and completed eight-drive N=6 finite-size hierarchy transfer. |
| Coupling and damping checkpoints | `data/checkpoints/`, `results/reproduced/`, `scripts/20_effective_coupling_scaling.py`, `scripts/submission/20_generate_damping_figure.py` | Secondary hybridization and dissipative-backaction diagnostics. |
| Channel and multichannel diagnostics | `results/reproduced/`, `data/prb_controls/`, Gate B2/C1 records | Prepared-mechanism benchmarks and explicit validity/breakdown tests, not primary full-model evidence. |
| Gate A v2 | `protocols/gate_a_v2/`, `results/gate_a_v2/` | Earlier exact controls and source data retained for provenance. |

## 2. Gate A v3: exact full-model route

### 2.1 Frozen protocol and provenance

The protocol is [`protocols/gate_a_v3/gate_a_v3_protocol.json`](../protocols/gate_a_v3/gate_a_v3_protocol.json). It was committed before the new response calculations, and each result JSON records the protocol/script SHA-256, source Git commit, UTC run timestamps, exact command, and a self-excluding result hash. This is accurately described as a **prospectively frozen numerical protocol**, not as formal preregistration.

The current v3 result directory is:

```text
results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/
```

`MANIFEST.json` lists SHA-256 values for all thirteen new physical-result JSON files. The v3 audit separately records hashes of the two v2 source results reused as exact baselines.

### 2.2 Matching logic

No safe single constant-period line of the two-step closed-chain BDI classifier contains all four labels \((0,0),(1,0),(0,1),(1,1)\). Gate A v3 therefore avoids a falsely “matched” four-class comparison and instead uses two separate equal-period pairs:

| Pair | Same within-pair controls | Purpose |
|---|---|---|
| \((1,1)\) OBC versus \((0,1)\) OBC | \(T\), \(\Omega\), \(gT\), \(\gamma_1T\), total physical time, discard time, detuning grid, initial state | Vary \(\nu_0\) at \(\nu_\pi=1\). |
| \((1,0)\) OBC versus \((0,0)\) OBC | The same quantities | Vary \(\nu_0\) at \(\nu_\pi=0\). |

The second line rescales bare \(g\) and \(\gamma_1\), and doubles periods, so that its dimensionless couplings and physical observation time equal those of the production-period line. This directly repairs the factor-of-three period and bare-coupling mismatch in the prior trivial control.

### 2.3 Current numerical conclusions

The Gate A v3 audit reports all directional ratios in the protocol-declared orientation. The held-out \((1,1)\) same-drive comparison yields \(W_{\rm OBC}/W_{\rm PBC}=9537.44\), while the production profile has \(W_r(0)/W_r(2)=W_r(0)/W_r(3)=981.45\). These are exact finite-N=6, common-preparation full-model observations.

The four-class controls do not pass the declared descriptive \(\nu_\pi\)-grouping test: the two \(\nu_\pi=1\) spectra are not mutually closest in normalized shape. This rules out a universal \(\nu_\pi\)-determined lineshape claim. Separately, the sampled raw weights show a descriptive hierarchy: both sampled \(\nu_\pi=1\) drives exceed both sampled \(\nu_\pi=0\) drives, with the smallest \(\nu_\pi=1\) weight 118.7 times the largest \(\nu_\pi=0\) weight. Because the two sectors belong to different equal-period lines, Gate A v3 alone does not turn this observation into a causal invariant claim. The later response-blind Gate D1/D2 route tests only the finite N=4-to-N=6 persistence of a separately selected eight-drive hierarchy; its completed result is recorded in section 5.

### 2.4 Sampling/window controls

The 2-, 4-, and 8-samples-per-half-step calculations agree within a normalized-shape distance of 0.0011. A 40-period discard differs from the 20-period baseline by 0.0462, under the frozen 0.10 acceptance threshold, and retains \(W_{40T}/W_{20T}=0.932\). A deliberately early 8-period discard differs by 0.1769 in detailed shape and fails the frozen criterion, while retaining \(W_{8T}/W_{20T}=1.041\). The required disclosure is therefore sensitivity of **early-transient lineshape**, not instability of the late-window integrated response or time discretization. No unregistered discard scan was used to conceal that result.

## 3. Reproducing the audit

The selection and audit scripts are repository-relative:

```bash
python scripts/gate_a_v3/01_iso_period_bdi_control_search.py
python scripts/gate_a_v3/02_common_period_fourclass_search.py
python scripts/gate_a_v3/03_select_v3_controls.py
python scripts/gate_a_v3/20_audit_gate_a_v3.py
```

The full exact N=6 campaign is intentionally separate and expensive:

```bash
python scripts/gate_a_v3/10_run_full_model_v3.py
```

The runner refuses to start from a dirty Git working tree because the source commit is part of each result's provenance. Recalculation of the full campaign should be done only after reviewing the frozen protocol; it is not necessary for a reviewer to verify the committed manifest and audit.

## 4. Mechanism scans and reduced-model limitations

The coupling and damping campaigns answer mechanism questions only after the geometry result and interpretive controls are fixed. The resolved coupling scan establishes approximately linear response-doublet splitting over its accepted interval. At fixed contact and harmonic, the plotted \(g|B_{0\pi}|\) axis is a constant rescaling of bare \(g\); it does not independently validate an absolute projected matrix element or an all-coupling perturbative law. The damping checkpoint records a nonmonotonic loading--recovery crossover versus \(\gamma_1T\). Its interpretation as fast-defect elimination or Zeno-like decoupling is qualitative, not a fitted phase boundary.

The pair-plus-channel construction remains part of the scientific record but is not a general reduction for the common product state. Gate B2 shows that adding initial-support states can raise retained state weight above 0.94 while leaving a large full-spectrum shape error. Gate C1 shows that M=1 Fourier micromotion agrees closely with exact within-manifold micromotion but does not repair disagreement with the exact N=4 full model.

The formal N=6/N=8 \(K=2,4,6,8\) records use a Floquet-pair-prepared projected state, not the common-product Gate A v3 contract. They show one restricted \(g=0.08\) window in which the dominant numerical correction occurs from \(K=2\) to \(K=4\), together with an N=8, \(g=0.12\) counterexample in which all tested \(K=4\)--8 spaces remain nonpredictive. These records are validity diagnostics, not a second positive size-scaling claim. No N=8/N=10 extension of the common-preparation response is inferred from them.

## 5. Gate D1 correction and completed Gate D2

The frozen Gate D1 protocol assigns the factor-10 threshold only to its two fixed-\(\nu_0\) median ratios. Its separate all-point condition is directional: \(\min W_{\nu_\pi=1}>\max W_{\nu_\pi=0}\). The corrected audit reports 239.10, 4276.67 and 7.004, so the unchanged protocol, selected candidates, raw results and manifest satisfy the literal candidate-screen rule.

Gate D2 propagated exactly those eight response-blind-selected drives at N=6 from the public source-freeze commit. The final manifest and audit validate all result hashes, self hashes, task fields, N=4/N=6 grids, normalized shapes, recomputed weights, runner and helper hashes. The frozen transfer decision passes: the fixed-\(\nu_0\) median ratios are 409.536 and 5633.720, and the all-point ordering ratio is 12.048. The detailed decision and result boundary are in [`GATE_D2_RESULT_DECISION.md`](gate_a_v3/GATE_D2_RESULT_DECISION.md). This supports finite, sampled hierarchy persistence for the specified cross-period protocol, not a common-period causal law or thermodynamic invariant.

## 6. Supplemental checkpoint route

The original compact scripts remain usable for the historical prepared-pair evidence:

```bash
python scripts/10_double_boundary_localization.py
python scripts/20_effective_coupling_scaling.py
python scripts/30_channel_time_validation.py
python scripts/submission/20_generate_damping_figure.py --check-only
```

Their limitations are unchanged: a finite six-site response fit is not a thermodynamic localization length; a resolved-regime line in \(|gB_{0\pi}|\) is not a zero-coupling theorem; and an N=4 channel/time agreement is not a universal dissipative reduction. See [`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md) for the current claim boundaries.

## 7. Environment, integrity, and citation

The repository was tested with Python 3.11, NumPy, SciPy, and Matplotlib from `requirements.txt`. No external API key, remote numerical service, or commercial software is required.

For the cited clean commit, start with:

```bash
git status --short
sha256sum results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/*.json
```

The earlier manuscript version is archived at [Zenodo, DOI: 10.5281/zenodo.20685212](https://doi.org/10.5281/zenodo.20685212). Cite the Zenodo record and the specific repository commit/release used for analysis until a final article is available.

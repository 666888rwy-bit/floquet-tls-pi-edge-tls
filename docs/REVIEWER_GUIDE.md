# Reviewer guide: current claim-to-evidence map

This guide prioritizes the **current exact full-model evidence** and makes the numerical limitations as easy to audit as the positive results. The intended scientific standard is a conservative finite-system statement, not a universal Floquet-spectroscopy claim.

## Recommended 15-minute audit path

Begin with the Gate A v3 audit, then inspect the two figures and the matching protocol. These artifacts are versioned in the repository; no long propagation is required to check their hashes and stated numerical comparisons.

| Order | Artifact | What to verify | Permitted conclusion | Explicit boundary |
|---:|---|---|---|---|
| 1 | [`results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/MANIFEST.json`](../results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/MANIFEST.json) | Each of the 13 SHA-256 entries matches the committed JSON file. | The raw v3 numerical files are internally traceable. | Hash consistency is not an independent physical validation. |
| 2 | [`GATE_A_V3_AUDIT.md`](../results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_AUDIT.md) | Same-period matching, directional ratios, and stated failures. | The exact N=6 protocol gives drive-class-dependent and boundary-selective response. | It does not identify a unique invariant mechanism. |
| 3 | [`GATE_A_V3_CONTROLS.png`](../results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_CONTROLS.png) | Held-out OBC/PBC contrast and complete \(m=0,\ldots,5\) spatial profile. | The specified held-out drive exhibits a large finite-system OBC/PBC contrast and edge-to-interior profile. | Six sites do not provide a thermodynamic localization law. |
| 4 | [`GATE_A_V3_CONVERGENCE.png`](../results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_CONVERGENCE.png) | Sampling and discard-window distances relative to frozen baseline. | The standard 20-period and longer 40-period windows, plus the sampling-density test, are mutually compatible. | The 8-period discard changes detailed early-transient lineshape, while its integrated weight remains close to baseline. |
| 5 | [`GATE_B_C_ROUTE_DECISION.md`](gate_a_v2/GATE_B_C_ROUTE_DECISION.md) | Why the reduced model was not scaled further. | The pair/manifold model is preparation-conditional. | It must not be advertised as a general quantitative full-model reduction. |

## Matched-control design

No safe single constant-period line of the present two-step closed-chain classifier contains all \((0,0),(1,0),(0,1),(1,1)\) labels. Gate A v3 therefore makes two separate pairwise comparisons rather than masking the mismatch:

| Pair | Invariants | Matching within pair | Purpose |
|---|---|---|---|
| \((1,1)\) versus \((0,1)\) | \(\nu_\pi=1\) in both drives | \(T\), \(\Omega\), \(gT\), \(\gamma_1T\), total time, readout grid, and common preparation | Change \(\nu_0\) at fixed \(\nu_\pi\). |
| \((1,0)\) versus \((0,0)\) | \(\nu_\pi=0\) in both drives | The same set of dimensionless and physical-time controls | Change \(\nu_0\) at fixed \(\nu_\pi\). |

The four-class data do **not** exhibit the predeclared normalized-shape grouping of the two \(\nu_\pi=1\) cases. A reviewer should regard this as a transparent negative inference test: it rules out a universal \(\nu_\pi\)-determined lineshape claim rather than being discarded. Separately, the sampled raw weights exhibit a descriptive hierarchy in which both \(\nu_\pi=1\) points exceed both \(\nu_\pi=0\) points; see `GATE_A_V3_WEIGHT_STRATIFICATION.png`. Because those sectors lie on different matched-period lines, this amplitude separation is exploratory and motivates a new multi-point frozen test rather than a retrospective invariant claim.

## Secondary mechanism evidence

The original checkpoint scripts are retained as supplemental mechanism and diagnostic material. They do not supersede Gate A v3 for the common physical preparation.

| Supplementary question | Artifact | Scope limit |
|---|---|---|
| Boundary response profile under the original checkpoint preparation | `scripts/10_double_boundary_localization.py` | Do not equate its fitted response length with a thermodynamic edge-mode length. |
| Resolved doublet versus selected \(|gB_{0\pi}|\) | `scripts/20_effective_coupling_scaling.py` | An empirical prepared-pair resolved-regime relation, not a universal coupling theorem. |
| N=4 channel/time comparison | `scripts/30_channel_time_validation.py` | A targeted channel mechanism test, not a general full-model reduction. |
| Multichannel limits | `results/gate_a_v2/.../gate_b2/` and `gate_c1/` | Initial-support and micromotion extensions do not recover common-preparation full spectra. |

## Minimal integrity checklist

```bash
git status --short
sha256sum results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/*.json
python scripts/gate_a_v3/20_audit_gate_a_v3.py
```

For the cited clean commit, `git status --short` should return no output before rerunning scripts. The audit script is read-only with respect to physical data; it recreates the figures and audit JSON from committed raw result files.

> The appropriate high-level statement is: **in a specified finite Floquet–Lindblad protocol, common-preparation TLS response is boundary-selective and drive-class-dependent. The sampled raw weights display an exploratory \(\nu_\pi\)-sector separation, whereas the available controls do not establish a unique \(\nu_\pi\)-controlled lineshape or causal law.**

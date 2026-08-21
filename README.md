# Local dissipative probing in a finite Floquet Ising chain

> **Reviewer-facing exact finite-system controls, frozen numerical protocols, and reproducible code for a periodically driven Ising chain locally coupled to an amplitude-damped TLS.**

This repository supports a manuscript in preparation on finite Floquet–Lindblad spectroscopy. Its principal result is an **exact common-preparation full-model comparison**: the TLS response is strongly boundary-selective for specified closed-chain BDI-labelled drives, while the data do not justify a thermodynamic-limit, phase-boundary, universal-effective-theory, or uniquely \(\nu_\pi\)-controlled response claim.

## Start here: Gate A v3 reviewer route

Gate A v3 is the current evidence hierarchy. Its protocol was prospectively frozen in a public commit before new full-model responses were run. Every new JSON result carries protocol/script hashes, a Git commit, UTC timestamps, and a self-excluding content hash.

| Question | Primary artifact | What it establishes | Required limitation |
|---|---|---|---|
| Are the new full-model responses traceable? | [`GATE_A_V3_AUDIT.md`](results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_AUDIT.md) and `MANIFEST.json` | The thirteen new result hashes match the frozen manifest. | The numerical protocol is **prospectively frozen**, not formally preregistered. |
| Is there finite-system boundary selectivity without pair preparation? | [`GATE_A_V3_CONTROLS.png`](results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_CONTROLS.png) | A held-out \((1,1)\) OBC drive has \(W_{\rm OBC}/W_{\rm PBC}=9537.44\) for the declared finite protocol. | This does not prove a thermodynamic boundary law or isolate one invariant. |
| Does the full common-preparation response have an edge-to-interior spatial profile? | Same control figure and `production_spatial_m*.json` | The exact N=6 profile is reflection symmetric, with \(W_r(0)/W_r(2)=981.45\). | No localization-length fit or asymptotic scaling is claimed from six sites. |
| Do matched BDI drive controls identify \(\nu_\pi\) as the unique cause? | `nu01_OBC_m0.json`, `nu10_OBC_m0.json`, `nu00_OBC_m0.json` and the v3 audit | The controls are matched in \(T\), \(gT\), \(\gamma_1T\), and physical time within each pair. | The frozen \(\nu_\pi\)-grouping check fails; do **not** claim \(\nu_\pi\)-specific TLS spectroscopy. |
| Are results stable to routine numerical choices? | [`GATE_A_V3_CONVERGENCE.png`](results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_CONVERGENCE.png) | Two-versus-four-versus-eight samples per half step and a 40-period discard are stable. | An 8-period discard fails the frozen shape criterion; conclusions are window-sensitive to early readout. |

The concise claim-to-file map is in [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md), and the complete reproducibility conventions are in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Important interpretation boundary

The repository also contains the earlier local Floquet-pair and multichannel analyses. They are retained because they document a useful deliberately prepared coherence mechanism and a transparent failed reduction route. They are **not** the primary evidence for the common-product-state full-model result.

Gate B2 shows that the common \(|\uparrow_z\rangle^{\otimes N}\) preparation occupies many Floquet states, so an initial-support-aware \(K=16\) static manifold retains weight but not the exact full-model spectral shape. Gate C1 then shows that adding \(n=\pm1,\pm2\) micromotion harmonics converges within the truncated N=4 subspace but does not repair its discrepancy from the exact full model. Consequently, this repository does not claim a generally controlled minimal Floquet manifold for TLS spectroscopy from arbitrary physical preparations.

## Repository map

| Path | Purpose |
|---|---|
| `protocols/gate_a_v3/` | Frozen Gate A v3 common-preparation and matched-control protocol. |
| `scripts/gate_a_v3/` | Closed-chain BDI selection, exact full-model runner, and read-only audit scripts. |
| `results/gate_a_v3/` | Versioned Gate A v3 raw JSON, manifest hashes, audit, and figures. |
| `protocols/gate_a_v2/`, `scripts/gate_a_v2/`, `results/gate_a_v2/` | Gate A v2 controls plus Gate B/C reduction diagnostics and their limits. |
| `scripts/`, `data/checkpoints/`, `notebooks/` | Earlier compact checkpoint analyses and original workflow records. |
| `docs/` | Reviewer guide, reproducibility protocol, data dictionary, and evidence-boundary documents. |

## Re-running Gate A v3

The production protocol and code are committed before running. The exact N=6 campaign is intentionally expensive. From a clean clone at the cited commit, the following commands reproduce the selection/audit path; the full runner is included for full recalculation rather than casual laptop use.

```bash
python scripts/gate_a_v3/01_iso_period_bdi_control_search.py
python scripts/gate_a_v3/02_common_period_fourclass_search.py
python scripts/gate_a_v3/03_select_v3_controls.py
python scripts/gate_a_v3/20_audit_gate_a_v3.py
```

The full campaign command is:

```bash
python scripts/gate_a_v3/10_run_full_model_v3.py
```

It must be launched from a clean working tree because each run records its source commit. The code uses Python 3.11, NumPy, SciPy, and Matplotlib; see `requirements.txt`.

## Citation and availability

The earlier manuscript preprint is archived at [Zenodo](https://doi.org/10.5281/zenodo.20685212). Please cite the repository commit or release that you actually use, together with the Zenodo record until a final article is available. The repository is released under the [MIT License](LICENSE).

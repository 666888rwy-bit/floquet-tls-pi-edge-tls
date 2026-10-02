# Local dissipative probing in a finite Floquet Ising chain

> **Reviewer-facing exact finite-system controls, frozen numerical protocols, and reproducible code for a periodically driven Ising chain locally coupled to an amplitude-damped TLS.**

This repository supports a manuscript in preparation on finite Floquet–Lindblad spectroscopy. Its principal result is an **exact common-preparation full-model comparison**: the frequency-resolved TLS response is strongly boundary selective for the specified finite protocol. Same-period BDI-labelled controls then limit the interpretation, and a separately frozen response-blind eight-drive campaign tests only whether one sampled raw-weight hierarchy persists from N=4 to N=6. Coupling, damping, channel, and multichannel calculations are retained as mechanism or validity diagnostics; they do not replace the geometry evidence. The data do not justify a thermodynamic-limit, phase-boundary, universal-effective-theory, uniquely \(\nu_\pi\)-controlled, or many-body time-crystal claim.

## Manuscript evidence hierarchy

| Layer | Primary question | Evidence role |
|---|---|---|
| 1. Common protocol | Are the preparation, detector grid, windows, and comparisons fixed and traceable? | Establishes the common physical contract and numerical provenance. |
| 2. Boundary-selective response | Does the exact TLS response change between OBC/PBC and from edge to interior contacts? | Primary finite-system result. |
| 3. Interpretive limits | Is the normalized response fixed by \(\nu_\pi\) alone? | No for the sampled same-period controls; the spectra remain drive dependent. |
| 4. Frozen size transfer | Does the response-blind N=4 raw-weight hierarchy persist for the same eight drives at N=6? | Gate D2 passes this finite cross-period transfer test, without becoming a causal topological law. |
| 5. Mechanism and validity | How does the TLS hybridize, load the boundary response, and where do reduced descriptions fail? | Secondary coupling, damping, channel, and multichannel diagnostics. |

## Start here: primary Gate A v3 route

Gate A v3 is the starting point of the current evidence hierarchy. Its protocol was prospectively frozen in a public commit before new full-model responses were run. Every new JSON result carries protocol/script hashes, a Git commit, UTC timestamps, and a self-excluding content hash.

| Question | Primary artifact | What it establishes | Required limitation |
|---|---|---|---|
| Are the new full-model responses traceable? | [`GATE_A_V3_AUDIT.md`](results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_AUDIT.md) and `MANIFEST.json` | The thirteen new result hashes match the frozen manifest. | The numerical protocol is **prospectively frozen**, not formally preregistered. |
| Is there finite-system boundary selectivity without pair preparation? | [`GATE_A_V3_CONTROLS.png`](results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_CONTROLS.png) | A held-out \((1,1)\) OBC drive has \(W_{\rm OBC}/W_{\rm PBC}=9537.44\) for the declared finite protocol. | This does not prove a thermodynamic boundary law or isolate one invariant. |
| Does the full common-preparation response have an edge-to-interior spatial profile? | Same control figure and `production_spatial_m*.json` | The exact N=6 profile is reflection symmetric, with \(W_r(0)/W_r(2)=981.45\). | No localization-length fit or asymptotic scaling is claimed from six sites. |
| Do matched BDI drive controls identify \(\nu_\pi\) as the unique cause? | `nu01_OBC_m0.json`, `nu10_OBC_m0.json`, `nu00_OBC_m0.json` and the v3 audit | The controls are matched in \(T\), \(gT\), \(\gamma_1T\), and physical time within each pair; sampled \(\nu_\pi=1\) weights exceed sampled \(\nu_\pi=0\) weights. | The frozen \(\nu_\pi\)-lineshape grouping check fails. The weight separation is exploratory, not a passed invariant law. |
| Are results stable to routine numerical choices? | [`GATE_A_V3_CONVERGENCE.png`](results/gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_CONVERGENCE.png) | Two-versus-four-versus-eight samples per half step, and the 20T/40T late windows, are stable. | An 8-period discard changes the detailed early-transient lineshape, not the integrated response weight. |

The concise claim-to-file map is in [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md), the manuscript-facing claim-to-artifact map is in [`docs/CLAIM_TO_ARTIFACT.md`](docs/CLAIM_TO_ARTIFACT.md), the complete reproducibility conventions are in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md), and the machine-checkable record contract is in [`docs/RESULT_SCHEMA.md`](docs/RESULT_SCHEMA.md).

## Completed Gate D2 finite-size transfer test

The response-blind Gate D1 N=4 screen passes its literal frozen rule: the factor-10 threshold applies to the two fixed-\(\nu_0\) median ratios, whereas the separate all-point condition requires only \(\min W_{\nu_\pi=1}>\max W_{\nu_\pi=0}\). The corrected D1 audit preserves the protocol, raw results, selected candidates and manifest while documenting the superseded audit threshold.

Gate D2 then propagated the same eight field-by-field-matched drives at N=6 from the public source-freeze commit. Its final audit validates every result and passes both median-ratio conditions (409.536 and 5633.720) plus the all-point ordering ratio (12.048). The result therefore supports finite-size persistence of the sampled, \(\nu_\pi\)-associated raw-weight hierarchy for this fixed response-blind, cross-period protocol. See [`GATE_D2_RESULT_DECISION.md`](docs/gate_a_v3/GATE_D2_RESULT_DECISION.md). It does not establish a common-period causal law, a thermodynamic invariant, universal \(\pi\)-edge spectroscopy or a universal lineshape.

## Important interpretation boundary

The repository also contains the earlier local Floquet-pair and multichannel analyses. They are retained because they document a useful deliberately prepared coherence mechanism and a transparent failed reduction route. They are **not** the primary evidence for the common-product-state full-model result.

Gate B2 shows that the common \(|\uparrow_z\rangle^{\otimes N}\) preparation occupies many Floquet states, so an initial-support-aware \(K=16\) static manifold retains weight but not the exact full-model spectral shape. Gate C1 then shows that adding \(n=\pm1,\pm2\) micromotion harmonics converges within the truncated N=4 subspace but does not repair its discrepancy from the exact full model. Consequently, this repository does not claim a generally controlled minimal Floquet manifold for TLS spectroscopy from arbitrary physical preparations.

## Repository map

| Path | Purpose |
|---|---|
| `protocols/gate_a_v3/` | Frozen Gate A v3 common-preparation and matched-control protocol. |
| `protocols/gate_d1/`, `protocols/gate_d2/` | Corrected N=4 weight screen, frozen N=6 transfer protocol, and completed eight-drive N=6 evidence route. |
| `results/gate_d1/`, `results/gate_d2/` | Versioned N=4 candidate-screen records and completed N=6 transfer records with manifests. |
| `scripts/gate_a_v3/` | Closed-chain BDI selection, exact full-model runner, and read-only audit scripts. |
| `results/gate_a_v3/` | Versioned Gate A v3 raw JSON, manifest hashes, audit, and figures. |
| `protocols/gate_a_v2/`, `scripts/gate_a_v2/`, `results/gate_a_v2/` | Gate A v2 controls plus Gate B/C reduction diagnostics and their limits. |
| `scripts/`, `data/checkpoints/`, `notebooks/` | Earlier compact checkpoint analyses and original workflow records. |
| `manuscript/` | Current evidence-first LaTeX manuscript, Supplementary Material, and submission figures. |
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

It must be launched from a clean working tree because each run records its source commit. The full campaign is separate from the inexpensive submission verification route. The repository targets Python 3.11; use the exact package versions in `requirements-lock.txt` or `environment.yml` for submission checks.

## Submission-check route

From a clean checkout, validate every committed result and run the unit/regression tests without creating derived files:

```bash
python -m pip install -r requirements-lock.txt
python scripts/run_submission_checks.py --check-only
```

To regenerate deterministic audit figures and a hash manifest outside the versioned result directory, run:

```bash
python scripts/run_submission_checks.py --output-dir build/submission_checks
```

The generated files are intentionally placed in the ignored `build/` directory. This build includes deterministic N=4 channel--time and N=6 damping/backaction figures generated solely from committed records, in addition to the Gate A v3 and Gate D2 audits. See [`docs/ENVIRONMENT_AND_PROVENANCE.md`](docs/ENVIRONMENT_AND_PROVENANCE.md) for the environment policy, [`docs/CLAIM_TO_ARTIFACT.md`](docs/CLAIM_TO_ARTIFACT.md) for manuscript evidence boundaries, and [`docs/PUBLIC_RELEASE_CHECKLIST.md`](docs/PUBLIC_RELEASE_CHECKLIST.md) for the release procedure.

## Release preflight

Before creating a tagged submission release, verify the clean-tree policy, required metadata and all no-write checks:

```bash
python scripts/release_preflight.py
```

The preflight does not create a release. To require an exact Git tag after tagging, append `--require-tag`.

## Citation and availability

An [earlier manuscript preprint](https://doi.org/10.5281/zenodo.20685212) is retained as a historical record. It predates the common-product Gate A v3 controls and completed Gate D2 transfer, and its DOI does not archive the present manuscript or numerical evidence. For the current results, cite the exact repository commit used. [`CITATION.cff`](CITATION.cff) names the manuscript author but intentionally omits an archival DOI until a version-specific submission release exists. The repository is released under the [MIT License](LICENSE).

# Submission-release checklist

This repository is public and released under the [MIT License](../LICENSE).  It contains a reviewer-facing finite-system Floquet--Lindblad evidence hierarchy, versioned numerical records, and a compact Zenodo archive for the earlier manuscript record.  Before a new article submission or archival release, the project owner should complete the following version-specific checks.

| Release item | Current repository state | Required action before the next submission tag |
|---|---|---|
| Repository visibility and license | Public GitHub repository with `LICENSE` | Keep the repository public unless a journal or coauthor agreement requires a temporary change; do not change the license without coauthor approval. |
| Evidence hierarchy | Gate A v3 is the primary common-preparation full-model route; older prepared-pair and reduced-model routes are retained with explicit limitations | Keep README, reviewer guide, manuscript and release notes consistent about this hierarchy. |
| Numerical validation | Unit tests, N=4 benchmark regression checks, static checks, committed-result regression checks and `scripts/run_submission_checks.py` are provided | Run `ruff check scripts/gate_a_v3/result_validation.py scripts/run_submission_checks.py scripts/release_preflight.py scripts/submission tests` and `python scripts/run_submission_checks.py --check-only` from a clean clone before every tag. |
| Claim mapping | `docs/CLAIM_TO_ARTIFACT.md` maps each manuscript statement to source records and deterministic scripts | Verify that the manuscript contains no claim broader than the map permits, and retain the map in the tagged archive. |
| Derived figures | Audits and the committed-data N=4 mechanism renderer write reproducible files to `build/`, which is ignored by Git | Generate final manuscript figures from the tagged commit and retain the emitted `SUBMISSION_CHECKS_MANIFEST.json` with the submission package. |
| Environment | `requirements-lock.txt`, `environment.yml`, and `pyproject.toml` specify the submission test environment | Recreate the Python 3.11 environment in a clean location and record any approved dependency update in release notes. |
| Citation metadata | `CITATION.cff` references the current Zenodo DOI and existing Git author identity | Before final article submission, replace the Git alias with verified scholarly author names, ORCIDs, affiliations, the final software version and the final article DOI when available. |
| Zenodo record | DOI `10.5281/zenodo.20685212` is linked as the earlier archive | Create a new versioned Zenodo record from the exact `v1.0-submission` GitHub release; do not overwrite or silently repurpose the earlier archive. |
| Data redistribution | Compact checkpoints and versioned JSON results are committed | Confirm with all authors that the data are suitable for public redistribution, and include the manifest hashes in the release notes. |
| Authorship and disclosures | Not represented in code metadata beyond the existing Git identity | Confirm manuscript authorship, affiliations, funding, CRediT roles and conflict-of-interest statements independently of this repository. |

## Final release commands

From a clean checkout at the intended tag, run:

```bash
python -m pip install -r requirements-lock.txt
ruff check scripts/gate_a_v3/result_validation.py scripts/run_submission_checks.py scripts/release_preflight.py scripts/submission tests
python scripts/run_submission_checks.py --check-only
python scripts/release_preflight.py
python scripts/run_submission_checks.py --output-dir build/submission_checks
```

The first command installs the locked test dependencies. The static check then covers correctness-oriented quality rules for the submission infrastructure. The no-write audit verifies tests, historical result hashes and the N=4 mechanism benchmark without modifying records. The release preflight requires a clean work tree and validates the required metadata; after adding a release tag, rerun it with `--require-tag`. The final command creates reproducible audit and mechanism figures plus a `SUBMISSION_CHECKS_MANIFEST.json` inside the ignored build directory. The tag, Git commit, generated-manifest hash and new Zenodo DOI should be recorded together in the manuscript data-availability statement.

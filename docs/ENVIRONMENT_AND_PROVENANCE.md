# Environment and provenance policy

## Rebuilding the submission-check environment

The compact reviewer checks and committed-result tests are supported on Python 3.11. The exact package versions used for the current submission-check workflow are recorded in `requirements-lock.txt`, `environment.yml`, and `pyproject.toml`. A clean environment can be created with either a Python virtual environment or Conda; the preferred verification command is:

```bash
python -m pip install -r requirements-lock.txt
python scripts/run_submission_checks.py --check-only
```

The repository intentionally separates this inexpensive verification route from an exact N=6 production rerun. The latter remains computationally more expensive and must be launched only from a clean, tagged work tree after reviewing the frozen protocol.

## Result-level provenance

Every committed Gate A v3 result records its frozen protocol hash, runner script hash, source Git commit, command line, UTC start and finish times, task metadata, and a self-excluding canonical JSON hash. The runner now also records the Python version, platform and NumPy/SciPy/Matplotlib versions for any newly launched independent protocol.

The existing Gate A v3 result set predates this additional environment field. It must not be retroactively edited: the historical result hashes are part of the public evidence record. For the current manuscript, the locked submission-check environment verifies the derived figures and integrity checks, while the historical provenance fields identify the exact source code and protocol associated with the original full-model calculations.

## What a future numerical protocol must record

A new protocol must receive a new versioned JSON file and Git tag. It should record the complete task specification, initial preparation, protocol and script hashes, source commit, environment, command, timing, result self-hash and manifest hash. New calibration or null tests should be separately labelled as validation protocols and must not be merged into the prospectively frozen Gate A v3 evidence set.

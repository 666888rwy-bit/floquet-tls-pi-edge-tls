#!/usr/bin/env python3
"""Check whether a Floquet--TLS repository revision is ready to tag and archive.

The preflight never modifies numerical results or creates a release.  It validates
repository metadata and runs the no-write submission checks.  ``--allow-dirty`` is
provided only for development diagnostics; actual submission tags must be made
from a clean working tree.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    "LICENSE",
    "README.md",
    "CITATION.cff",
    "requirements-lock.txt",
    "environment.yml",
    "pyproject.toml",
    "docs/CLAIM_TO_ARTIFACT.md",
    "docs/ENVIRONMENT_AND_PROVENANCE.md",
    "docs/RESULT_SCHEMA.md",
    "scripts/run_submission_checks.py",
)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-dirty", action="store_true", help="Permit diagnostics on an uncommitted working tree; never use for a submission tag")
    parser.add_argument("--require-tag", action="store_true", help="Require that HEAD has an exact Git tag")
    parser.add_argument("--skip-submission-checks", action="store_true", help="Skip tests/audit only when they have already been recorded for the identical commit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    missing = [path for path in REQUIRED_PATHS if not (REPO / path).is_file()]
    if missing:
        raise SystemExit("Release preflight failed: missing required files: " + ", ".join(missing))

    citation = (REPO / "CITATION.cff").read_text(encoding="utf-8")
    for required_field in ("cff-version:", "title:", "version:", "repository-code:", "license:"):
        if required_field not in citation:
            raise SystemExit(f"Release preflight failed: CITATION.cff is missing {required_field}")

    dirty = git("status", "--porcelain")
    if dirty and not args.allow_dirty:
        raise SystemExit("Release preflight failed: working tree is dirty. Commit or stash changes before tagging.")
    if args.require_tag:
        try:
            tag = git("describe", "--exact-match", "--tags", "HEAD")
        except subprocess.CalledProcessError as exc:
            raise SystemExit("Release preflight failed: HEAD has no exact release tag") from exc
    else:
        tag = None

    if not args.skip_submission_checks:
        subprocess.run([sys.executable, "scripts/run_submission_checks.py", "--check-only"], cwd=REPO, check=True)

    payload = {
        "schema": "floquet_tls_release_preflight_v1",
        "git_commit": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "exact_tag": tag,
        "working_tree_clean": not bool(dirty),
        "submission_checks_run": not args.skip_submission_checks,
        "required_paths": list(REQUIRED_PATHS),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

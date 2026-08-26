from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/release_preflight.py"


def test_release_preflight_validates_metadata_in_development_mode() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT.relative_to(REPO)), "--allow-dirty", "--skip-submission-checks"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    )
    start = completed.stdout.find("{")
    payload = json.loads(completed.stdout[start:])
    assert payload["schema"] == "floquet_tls_release_preflight_v1"
    assert payload["git_commit"]
    assert "docs/CLAIM_TO_ARTIFACT.md" in payload["required_paths"]
    assert payload["submission_checks_run"] is False

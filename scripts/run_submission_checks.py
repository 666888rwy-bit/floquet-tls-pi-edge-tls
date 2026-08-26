#!/usr/bin/env python3
"""Run the reproducibility checks required for the Floquet--TLS submission build.

The command validates committed numerical records without rerunning the expensive
N=6 campaign.  In normal mode it writes derived audit figures and an integrity
manifest to ``build/submission_checks``; ``--check-only`` performs no writes and
is suitable for continuous integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "scripts/gate_a_v3/20_audit_gate_a_v3.py"
MECHANISM_FIGURES = REPO / "scripts/submission/10_generate_mechanism_figures.py"
D2_AUDIT = REPO / "scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py"
D2_MANIFEST = REPO / "results/gate_d2/gate_d2.0__e615217fa606/MANIFEST.json"
DEFAULT_OUTPUT = REPO / "build/submission_checks"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=REPO, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Directory for derived figures and manifest")
    parser.add_argument("--check-only", action="store_true", help="Run tests and record validation without writing any output")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest; intended only for a local figure-refresh after tests have passed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.skip_tests:
        run([sys.executable, "-m", "pytest", "-q"])

    audit_command = [sys.executable, str(AUDIT.relative_to(REPO))]
    mechanism_command = [sys.executable, str(MECHANISM_FIGURES.relative_to(REPO))]
    if args.check_only:
        audit_command.append("--check-only")
        mechanism_command.append("--check-only")
    else:
        output = args.output_dir.resolve()
        audit_command.extend(["--output-dir", str(output / "gate_a_v3_audit")])
        mechanism_command.extend(["--output-dir", str(output / "mechanism_figures")])
    run(audit_command)
    run(mechanism_command)

    if D2_MANIFEST.exists():
        d2_command = [sys.executable, str(D2_AUDIT.relative_to(REPO))]
        if args.check_only:
            d2_command.append("--check-only")
        else:
            d2_command.extend(["--output-dir", str(args.output_dir.resolve() / "gate_d2_audit")])
        run(d2_command)
    else:
        print("Gate D2 final manifest is absent; validated the frozen source route only.")

    if args.check_only:
        print("Submission checks completed without writing outputs.")
        return

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    artifacts = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = {
        "schema": "floquet_tls_submission_checks_v1",
        "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "artifacts": {str(path.relative_to(REPO)): sha256(path) for path in artifacts},
    }
    manifest_path = output / "SUBMISSION_CHECKS_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Submission checks completed. Derived artifacts: {output.relative_to(REPO)}")


if __name__ == "__main__":
    main()

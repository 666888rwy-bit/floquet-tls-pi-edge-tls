#!/usr/bin/env python3
"""Run the compact reviewer-facing reproducibility checks in a fixed order."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = {
    "localization": ROOT / "scripts" / "10_double_boundary_localization.py",
    "scaling": ROOT / "scripts" / "20_effective_coupling_scaling.py",
    "channel": ROOT / "scripts" / "30_channel_time_validation.py",
    "limit": ROOT / "scripts" / "90_multipo_effective_model_limit.py",
    "reference": ROOT / "scripts" / "00_reproduce_n6_reference.py",
}


def run(label: str) -> None:
    script = SCRIPTS[label]
    print(f"\n=== {label}: {script.name} ===", flush=True)
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run compact Floquet–TLS reviewer checks from the repository root."
    )
    parser.add_argument(
        "--include-limit",
        action="store_true",
        help="Also run the interior high-bare-coupling effective-model limitation diagnostic.",
    )
    parser.add_argument(
        "--include-reference",
        action="store_true",
        help="Also run the slower direct N=6 propagation/reference-point check.",
    )
    args = parser.parse_args()

    for label in ("localization", "scaling", "channel"):
        run(label)
    if args.include_limit:
        run("limit")
    if args.include_reference:
        run("reference")
    print("\nReviewer checks completed. Inspect results/reproduced/ and docs/REVIEWER_GUIDE.md.")


if __name__ == "__main__":
    main()

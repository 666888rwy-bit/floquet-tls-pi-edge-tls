from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "results/reproduced/C_N4_channel_time_validation_results.json"
SCRIPT = REPO / "scripts/submission/10_generate_mechanism_figures.py"


def load_benchmark() -> dict:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def test_committed_n4_channel_benchmark_matches_reference_values() -> None:
    record = load_benchmark()
    channel = record["channel"]
    fit = record["time_fit_primary"]
    assert record["parameters"]["N"] == 4
    assert channel["pair_conjugacy_error"] < 1e-12
    assert channel["tau_periods"] == pytest.approx(17.4931177194096, rel=1e-12)
    assert channel["delta_per_period"] == pytest.approx(0.10360358375836677, rel=1e-12)
    assert fit["success"] is True
    assert fit["n_start"] == 8
    assert fit["tau_periods"] == pytest.approx(16.091585771775808, rel=1e-12)
    assert fit["delta_per_period"] == pytest.approx(0.1167385240056578, rel=1e-12)


def test_n4_time_fit_remains_a_qualified_channel_benchmark() -> None:
    record = load_benchmark()
    comparison = record["relative_comparison"]
    assert 0.85 < comparison["tau_fit_over_channel"] < 1.15
    assert 0.85 < comparison["delta_fit_over_channel"] < 1.20
    assert record["time_fit_primary"]["rmse"] < 0.04


def test_mechanism_figure_check_only_validates_committed_source_without_writing(tmp_path: Path) -> None:
    command = [
        sys.executable,
        str(SCRIPT.relative_to(REPO)),
        "--check-only",
        "--output-dir",
        str(tmp_path / "must_not_exist"),
    ]
    completed = subprocess.run(command, cwd=REPO, check=True, capture_output=True, text=True)
    assert '"schema": "floquet_tls_n4_mechanism_figure_v1"' in completed.stdout
    assert "prepared mechanism diagnostic" in completed.stdout
    assert not (tmp_path / "must_not_exist").exists()

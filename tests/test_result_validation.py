from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

from scripts.gate_a_v3.result_validation import (
    ResultValidationError,
    normalized_shape_distance,
    validate_matching_grids,
    validate_result_record,
)

REPO = Path(__file__).resolve().parents[1]
V3 = REPO / "results/gate_a_v3/gate_a_v3.0__1b3dd5130c77"
PROTOCOL_SHA = "1b3dd5130c77050af93c03463f6302259b14816870cfee2229d71eb7bedd8a27"


def load_v3(name: str) -> dict:
    return json.loads((V3 / name).read_text(encoding="utf-8"))


def test_committed_v3_result_is_self_consistent() -> None:
    diagnostics = validate_result_record(load_v3("nu01_OBC_m0.json"), expected_protocol_sha256=PROTOCOL_SHA)
    assert diagnostics["points"] == 11.0
    assert diagnostics["spectral_weight"] > 0.0
    assert diagnostics["peak_response"] > 0.0


def test_mutated_result_hash_is_rejected() -> None:
    record = load_v3("nu01_OBC_m0.json")
    record["raw_A_TLS"][0] += 1e-6
    with pytest.raises(ResultValidationError, match="normalized_shape|self hash"):
        validate_result_record(record, expected_protocol_sha256=PROTOCOL_SHA)


def test_mismatched_grids_are_rejected() -> None:
    left = load_v3("nu01_OBC_m0.json")
    right = deepcopy(left)
    right["ratios"][0] += 1e-3
    with pytest.raises(ResultValidationError, match="identical detuning-ratio grid"):
        validate_matching_grids(left, right)


def test_committed_spatial_profile_respects_reflection_symmetry() -> None:
    weights = []
    for contact in range(1, 6):
        diagnostics = validate_result_record(load_v3(f"production_spatial_m{contact}.json"), expected_protocol_sha256=PROTOCOL_SHA)
        weights.append(diagnostics["spectral_weight"])
    production_m0 = json.loads(
        (REPO / "results/gate_a_v2/gate_a_v2.0__00d3477cc81e/primary_controls/topological_obc_production_v2__m0.json").read_text(encoding="utf-8")
    )
    m0_weight = float(
        np.trapezoid(
            np.asarray(production_m0["raw_A_TLS"], dtype=float) ** 2,
            np.asarray(production_m0["detuning_ratios_omega_d_over_Omega_over_2"], dtype=float),
        )
    )
    assert m0_weight == pytest.approx(weights[-1], rel=1e-12, abs=1e-15)
    assert weights[0] == pytest.approx(weights[-2], rel=1e-12, abs=1e-15)
    assert weights[1] == pytest.approx(weights[-3], rel=1e-12, abs=1e-15)


def test_committed_d8_variant_remains_outside_frozen_shape_threshold() -> None:
    baseline = json.loads(
        (REPO / "results/gate_a_v2/gate_a_v2.0__00d3477cc81e/primary_controls/topological_obc_production_v2__m0.json").read_text(encoding="utf-8")
    )
    d8 = load_v3("convergence_s4_d8.json")
    assert normalized_shape_distance(baseline, d8) > 0.10


def test_audit_check_only_succeeds_without_writing_build_outputs(tmp_path: Path) -> None:
    command = [
        sys.executable,
        "scripts/gate_a_v3/20_audit_gate_a_v3.py",
        "--check-only",
        "--output-dir",
        str(tmp_path / "must_not_exist"),
    ]
    completed = subprocess.run(command, cwd=REPO, check=True, capture_output=True, text=True)
    assert '"schema": "gate_a_v3_audit_v3"' in completed.stdout
    assert not (tmp_path / "must_not_exist").exists()

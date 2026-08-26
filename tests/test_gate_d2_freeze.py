from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

from scripts.gate_a_v3.gate_d2_validation import (
    ResultValidationError,
    canonical_sha256,
    sha256_path,
    validate_authorization,
    validate_gate_d2_result,
)

REPO = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = REPO / "protocols/gate_d2/gate_d2_n6_nupi_weight_transfer_protocol.json"
RUNNER = REPO / "scripts/gate_a_v3/33_run_gate_d2_n6_weight_transfer.py"
HELPER = REPO / "scripts/gate_a_v2/10_full_model_common_preparation.py"
D1_AUDIT = REPO / "results/gate_d1/gate_d1.0__6d3a08047527/GATE_D1_N4_WEIGHT_AUDIT.json"
D2_PROTOCOL_SHA = "e615217fa6063ff9c2d400cb927f9d1963d4a29386047fa3c6ae1c40335cd72e"
D1_AUDIT_SHA = "34961d819b8dd4cf1f1aaec519161e3d0a2674a5a043e660ad05d00770357f3a"


def load_protocol() -> dict:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def synthetic_result() -> tuple[dict, dict, dict]:
    protocol = load_protocol()
    task = protocol["selected_drives"][0]
    common = protocol["common_physical_protocol"]
    ratios = np.asarray(common["detuning_ratios_omega_d_over_Omega_over_2"], dtype=float)
    raw = np.linspace(0.01, 0.02, ratios.size)
    record = {
        "schema": "gate_d2_n6_full_model_result_v1",
        "task": task,
        "common_protocol": {
            "N_chain": common["N_chain"],
            "boundary": common["boundary"],
            "TLS_contact_site": common["TLS_contact_site"],
            "initial_chain_state": common["initial_chain_state"],
            "initial_TLS_state": common["initial_TLS_state"],
            "floquet_pair_selected": False,
            "B0_constructed": False,
            "gT_target": common["gT_target"],
            "gamma1T_target": common["gamma1T_target"],
            "periods": common["periods"],
            "discard_periods": common["discard_periods"],
            "samples_per_half_step": common["samples_per_half_step"],
        },
        "timing": {
            "T": task["T"],
            "Omega": task["Omega"],
            "g": common["gT_target"] / task["T"],
            "gamma1": common["gamma1T_target"] / task["T"],
            "gT": common["gT_target"],
            "gamma1T": common["gamma1T_target"],
            "total_time": common["periods"] * task["T"],
        },
        "ratios": ratios.tolist(),
        "raw_A_TLS": raw.tolist(),
        "normalized_shape": (raw / np.linalg.norm(raw)).tolist(),
        "W_r": float(np.trapezoid(raw**2, ratios)),
        "provenance": {
            "protocol_sha256": sha256_path(PROTOCOL_PATH),
            "script_sha256": sha256_path(RUNNER),
            "helper_sha256": sha256_path(HELPER),
            "repository_url": "https://example.invalid/frozen.git",
            "git_commit": "0" * 40,
            "public_commit_refs": ["refs/heads/main"],
            "run_started_utc": "2026-08-25T00:00:00Z",
            "run_finished_utc": "2026-08-25T00:01:00Z",
            "command": [sys.executable, str(RUNNER.relative_to(REPO))],
            "environment": {
                "python": sys.version,
                "python_implementation": "CPython",
                "platform": "test",
                "machine": "test",
                "processor": "test",
                "package_versions": {
                    "numpy": np.__version__,
                    "scipy": "test",
                    "matplotlib": "test",
                },
                "blas_lapack_configuration": "test BLAS",
                "thread_environment": {},
            },
        },
    }
    record["result_sha256_excluding_self"] = canonical_sha256(record)
    return record, task, protocol


def validate(record: dict, task: dict, protocol: dict) -> dict[str, float]:
    return validate_gate_d2_result(
        record,
        expected_task=task,
        protocol=protocol,
        protocol_sha256=sha256_path(PROTOCOL_PATH),
        runner_sha256=sha256_path(RUNNER),
        helper_sha256=sha256_path(HELPER),
    )


def test_gate_d2_protocol_and_corrected_audit_hashes_are_frozen() -> None:
    assert sha256_path(PROTOCOL_PATH) == D2_PROTOCOL_SHA
    assert sha256_path(D1_AUDIT) == D1_AUDIT_SHA


def test_gate_d2_authorization_and_fieldwise_drive_transfer() -> None:
    authorization = validate_authorization(protocol=load_protocol(), repository=REPO)
    assert authorization["selected_drives_exact_match"] is True
    assert authorization["gate_d1_screen_pass"] is True


def test_fieldwise_drive_drift_is_rejected() -> None:
    protocol = load_protocol()
    protocol["selected_drives"][0]["alpha_over_pi"] += 1e-9
    with pytest.raises(ResultValidationError, match="field-by-field"):
        validate_authorization(protocol=protocol, repository=REPO)


def test_complete_gate_d2_schema_validation() -> None:
    record, task, protocol = synthetic_result()
    diagnostics = validate(record, task, protocol)
    assert diagnostics["points"] == 11.0
    assert diagnostics["spectral_weight"] > 0.0


@pytest.mark.parametrize("mutation", ["grid_length", "nonfinite", "shape_definition", "helper_hash"])
def test_invalid_gate_d2_records_are_rejected(mutation: str) -> None:
    record, task, protocol = synthetic_result()
    bad = deepcopy(record)
    if mutation == "grid_length":
        bad["raw_A_TLS"] = bad["raw_A_TLS"][:-1]
    elif mutation == "nonfinite":
        bad["raw_A_TLS"][0] = float("nan")
    elif mutation == "shape_definition":
        bad["normalized_shape"][0] += 0.01
    else:
        bad["provenance"]["helper_sha256"] = "f" * 64
    bad["result_sha256_excluding_self"] = canonical_sha256(
        {key: value for key, value in bad.items() if key != "result_sha256_excluding_self"}
    )
    with pytest.raises(ResultValidationError):
        validate(bad, task, protocol)


def output_snapshot(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {
        str(candidate.relative_to(path)): sha256_path(candidate)
        for candidate in sorted(path.rglob("*"))
        if candidate.is_file()
    }


def test_gate_d2_dry_run_lists_only_frozen_ids_and_writes_nothing() -> None:
    protocol = load_protocol()
    output = REPO / "results/gate_d2" / f"{protocol['protocol_version']}__{sha256_path(PROTOCOL_PATH)[:12]}"
    before = output_snapshot(output)
    completed = subprocess.run(
        [sys.executable, str(RUNNER.relative_to(REPO)), "--dry-run"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    )
    plan = json.loads(completed.stdout)
    assert plan["requested"] == [task["id"] for task in protocol["selected_drives"]]
    assert plan["authorization"]["selected_drives_exact_match"] is True
    assert output_snapshot(REPO / plan["output_dir"]) == before

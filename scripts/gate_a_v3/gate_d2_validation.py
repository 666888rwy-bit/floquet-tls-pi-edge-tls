"""Strict, propagation-free validation helpers for the frozen Gate D2 campaign."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.metadata as metadata
import io
import json
import os
import platform
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np

try:  # Package import in tests; direct import when a numbered script is executed.
    from .result_validation import ResultValidationError, canonical_sha256
except ImportError:  # pragma: no cover - exercised by command-line entry points
    from result_validation import ResultValidationError, canonical_sha256


GATE_D2_RESULT_SCHEMA = "gate_d2_n6_full_model_result_v1"
RUNTIME_PACKAGES = ("numpy", "scipy", "matplotlib")
THREAD_ENVIRONMENT_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def runtime_environment() -> dict[str, Any]:
    """Record the numerical runtime, including the BLAS configuration."""
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        np.show_config()
    versions: dict[str, str] = {}
    for package in RUNTIME_PACKAGES:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "not-installed"
    return {
        "python": sys.version.replace("\n", " "),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "package_versions": versions,
        "blas_lapack_configuration": stream.getvalue().strip(),
        "thread_environment": {
            key: os.environ.get(key) for key in THREAD_ENVIRONMENT_KEYS
        },
    }


def validate_authorization(
    *, protocol: Mapping[str, Any], repository: Path
) -> dict[str, Any]:
    """Verify Gate D1 evidence anchors and exact D1-to-D2 task transfer."""
    authorization = protocol.get("authorization")
    if not isinstance(authorization, Mapping):
        raise ResultValidationError("Gate D2 protocol lacks authorization metadata")

    d1_protocol_path = repository / str(authorization["source_gate_d1_protocol"])
    d1_audit_path = repository / str(authorization["source_corrected_gate_d1_audit"])
    observed_protocol_sha = sha256_path(d1_protocol_path)
    observed_audit_sha = sha256_path(d1_audit_path)
    if observed_protocol_sha != authorization.get("source_gate_d1_protocol_sha256"):
        raise ResultValidationError("Gate D1 protocol SHA-256 does not match the Gate D2 anchor")
    if observed_audit_sha != authorization.get("source_corrected_gate_d1_audit_sha256"):
        raise ResultValidationError("Corrected Gate D1 audit SHA-256 does not match the Gate D2 anchor")

    d1_protocol = load_json(d1_protocol_path)
    d1_audit = load_json(d1_audit_path)
    if d1_protocol.get("selected_drives") != protocol.get("selected_drives"):
        raise ResultValidationError(
            "Gate D2 selected_drives are not field-by-field identical to frozen Gate D1"
        )
    if d1_audit.get("schema") != "gate_d1_n4_weight_audit_v2":
        raise ResultValidationError("Gate D2 requires the corrected Gate D1 v2 audit schema")
    decision = d1_audit.get("frozen_weight_screen", {})
    if decision.get("screen_pass") is not True:
        raise ResultValidationError("Corrected Gate D1 audit does not authorize Gate D2")
    if decision.get("frozen_condition_2_all_nupi1_weights_exceed_all_nupi0") is not True:
        raise ResultValidationError("Corrected Gate D1 all-point ordering is absent or false")

    return {
        "source_gate_d1_protocol_sha256": observed_protocol_sha,
        "source_corrected_gate_d1_audit_sha256": observed_audit_sha,
        "selected_drives_exact_match": True,
        "gate_d1_screen_pass": True,
    }


def _finite_vector(record: Mapping[str, Any], field: str) -> np.ndarray:
    if field not in record:
        raise ResultValidationError(f"Missing required Gate D2 result field: {field}")
    values = np.asarray(record[field], dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ResultValidationError(f"{field} must be a one-dimensional vector")
    if not np.all(np.isfinite(values)):
        raise ResultValidationError(f"{field} contains non-finite values")
    return values


def _finite_scalar(value: Any, field: str) -> float:
    if not isinstance(value, (int, float)) or not np.isfinite(value):
        raise ResultValidationError(f"{field} must be a finite scalar")
    return float(value)


def validate_gate_d2_result(
    record: Mapping[str, Any],
    *,
    expected_task: Mapping[str, Any],
    protocol: Mapping[str, Any],
    protocol_sha256: str,
    runner_sha256: str,
    helper_sha256: str,
    expected_git_commit: str | None = None,
    require_self_hash: bool = True,
) -> dict[str, float]:
    """Validate every deterministic field of one N=6 Gate D2 result."""
    if record.get("schema") != GATE_D2_RESULT_SCHEMA:
        raise ResultValidationError("Unexpected Gate D2 result schema")
    if record.get("task") != dict(expected_task):
        raise ResultValidationError("Gate D2 task metadata differs from the frozen task")

    common = protocol["common_physical_protocol"]
    stored_common = record.get("common_protocol")
    if not isinstance(stored_common, Mapping):
        raise ResultValidationError("Gate D2 common_protocol must be an object")
    exact_common = {
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
    }
    if dict(stored_common) != exact_common:
        raise ResultValidationError("Stored Gate D2 common protocol differs from the freeze")

    ratios = _finite_vector(record, "ratios")
    raw = _finite_vector(record, "raw_A_TLS")
    shape = _finite_vector(record, "normalized_shape")
    expected_ratios = np.asarray(
        common["detuning_ratios_omega_d_over_Omega_over_2"], dtype=float
    )
    if ratios.shape != expected_ratios.shape or not np.array_equal(ratios, expected_ratios):
        raise ResultValidationError("Gate D2 ratio grid differs from the frozen protocol")
    if raw.shape != ratios.shape or shape.shape != ratios.shape:
        raise ResultValidationError("ratios, raw_A_TLS and normalized_shape lengths differ")
    if not np.all(np.diff(ratios) > 0.0):
        raise ResultValidationError("Gate D2 ratio grid must be strictly increasing")
    if np.any(raw < 0.0):
        raise ResultValidationError("raw_A_TLS must contain phasor moduli, not negative values")
    norm = float(np.linalg.norm(raw))
    if norm <= 0.0:
        raise ResultValidationError("raw_A_TLS cannot have zero norm")
    if not np.allclose(shape, raw / norm, rtol=1e-11, atol=1e-13):
        raise ResultValidationError("normalized_shape is inconsistent with raw_A_TLS")
    weight = float(np.trapezoid(raw**2, ratios))
    if not np.isclose(_finite_scalar(record.get("W_r"), "W_r"), weight, rtol=1e-11, atol=1e-13):
        raise ResultValidationError("W_r is inconsistent with the frozen grid and raw_A_TLS")

    timing = record.get("timing")
    if not isinstance(timing, Mapping):
        raise ResultValidationError("Gate D2 timing metadata must be an object")
    period = _finite_scalar(timing.get("T"), "timing.T")
    omega = _finite_scalar(timing.get("Omega"), "timing.Omega")
    if not np.isclose(period, expected_task["T"], rtol=0.0, atol=1e-12):
        raise ResultValidationError("Gate D2 period differs from the frozen task")
    if not np.isclose(omega, expected_task["Omega"], rtol=0.0, atol=1e-12):
        raise ResultValidationError("Gate D2 Omega differs from the frozen task")
    for field, target in (("gT", common["gT_target"]), ("gamma1T", common["gamma1T_target"])):
        if not np.isclose(_finite_scalar(timing.get(field), f"timing.{field}"), target, rtol=0.0, atol=1e-12):
            raise ResultValidationError(f"Gate D2 {field} differs from the frozen protocol")
    if not np.isclose(
        _finite_scalar(timing.get("total_time"), "timing.total_time"),
        common["periods"] * period,
        rtol=1e-12,
        atol=1e-12,
    ):
        raise ResultValidationError("Gate D2 total_time is inconsistent")

    provenance = record.get("provenance")
    if not isinstance(provenance, Mapping):
        raise ResultValidationError("Gate D2 provenance must be an object")
    expected_hashes = {
        "protocol_sha256": protocol_sha256,
        "script_sha256": runner_sha256,
        "helper_sha256": helper_sha256,
    }
    for key, expected in expected_hashes.items():
        if provenance.get(key) != expected:
            raise ResultValidationError(f"Gate D2 provenance {key} mismatch")
    if expected_git_commit is not None and provenance.get("git_commit") != expected_git_commit:
        raise ResultValidationError("Gate D2 result was produced from a different freeze commit")
    for key in (
        "repository_url",
        "git_commit",
        "public_commit_refs",
        "run_started_utc",
        "run_finished_utc",
        "command",
    ):
        if key not in provenance:
            raise ResultValidationError(f"Gate D2 provenance is missing {key}")
    public_refs = provenance["public_commit_refs"]
    if not isinstance(public_refs, list) or not public_refs or not all(
        isinstance(ref, str) and ref for ref in public_refs
    ):
        raise ResultValidationError("Gate D2 provenance lacks a verified public commit ref")
    environment = provenance.get("environment")
    if not isinstance(environment, Mapping):
        raise ResultValidationError("Gate D2 provenance is missing runtime environment")
    for key in (
        "python",
        "python_implementation",
        "platform",
        "package_versions",
        "blas_lapack_configuration",
        "thread_environment",
    ):
        if key not in environment:
            raise ResultValidationError(f"Gate D2 runtime environment is missing {key}")
    package_versions = environment["package_versions"]
    if not isinstance(package_versions, Mapping) or any(
        package not in package_versions for package in RUNTIME_PACKAGES
    ):
        raise ResultValidationError("Gate D2 package version metadata is incomplete")

    if require_self_hash:
        observed = record.get("result_sha256_excluding_self")
        payload = dict(record)
        payload.pop("result_sha256_excluding_self", None)
        if not isinstance(observed, str) or canonical_sha256(payload) != observed:
            raise ResultValidationError("Gate D2 result self hash mismatch")

    return {
        "points": float(ratios.size),
        "response_norm": norm,
        "spectral_weight": weight,
        "peak_response": float(np.max(raw)),
    }

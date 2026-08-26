"""Validation helpers for versioned Gate A v3 Floquet--TLS result records.

The functions in this module are deliberately dependency-light so that they can be
used both by the audit script and by the test suite without launching an expensive
full-model propagation.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

import numpy as np


class ResultValidationError(ValueError):
    """Raised when a committed numerical result violates its declared schema."""


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    """Return the canonical JSON SHA-256 used by the production runner."""
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _as_finite_vector(record: Mapping[str, Any], field: str) -> np.ndarray:
    if field not in record:
        raise ResultValidationError(f"Missing required field: {field}")
    values = np.asarray(record[field], dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ResultValidationError(f"{field} must be a one-dimensional vector with at least two entries")
    if not np.all(np.isfinite(values)):
        raise ResultValidationError(f"{field} contains non-finite values")
    return values


def result_ratios(record: Mapping[str, Any]) -> np.ndarray:
    """Return the declared detuning-ratio grid after schema validation.

    Gate A v3 uses ``ratios``; the committed v2 baselines use the longer
    ``detuning_ratios_omega_d_over_Omega_over_2`` field name.
    """
    if "ratios" in record:
        return _as_finite_vector(record, "ratios")
    return _as_finite_vector(record, "detuning_ratios_omega_d_over_Omega_over_2")


def result_response(record: Mapping[str, Any]) -> np.ndarray:
    """Return the non-negative TLS phasor amplitude grid after validation."""
    values = _as_finite_vector(record, "raw_A_TLS")
    if np.any(values < 0.0):
        raise ResultValidationError("raw_A_TLS must be non-negative because it stores a phasor modulus")
    return values


def validate_matching_grids(left: Mapping[str, Any], right: Mapping[str, Any]) -> np.ndarray:
    """Require two spectra to use exactly the same finite, increasing ratio grid."""
    grid_left = result_ratios(left)
    grid_right = result_ratios(right)
    if grid_left.shape != grid_right.shape or not np.array_equal(grid_left, grid_right):
        raise ResultValidationError("Compared spectra do not share an identical detuning-ratio grid")
    if not np.all(np.diff(grid_left) > 0.0):
        raise ResultValidationError("Detuning-ratio grid must be strictly increasing")
    return grid_left


def validate_result_record(
    record: Mapping[str, Any],
    *,
    expected_task: Mapping[str, Any] | None = None,
    expected_protocol_sha256: str | None = None,
    require_self_hash: bool = True,
) -> dict[str, float]:
    """Validate a Gate A v3 full-model JSON record and return derived diagnostics.

    This checks only deterministic record consistency.  It does not claim to
    independently validate the physics of a completed calculation.
    """
    if record.get("schema") != "gate_a_v3_full_model_result_v1":
        raise ResultValidationError("Unexpected or missing Gate A v3 result schema")
    if not isinstance(record.get("task"), dict):
        raise ResultValidationError("Result task metadata must be a JSON object")
    if expected_task is not None and record["task"] != dict(expected_task):
        raise ResultValidationError("Result task metadata does not match the requested task")

    ratios = result_ratios(record)
    response = result_response(record)
    if ratios.size != response.size:
        raise ResultValidationError("ratios and raw_A_TLS must have the same length")
    if not np.all(np.diff(ratios) > 0.0):
        raise ResultValidationError("Detuning-ratio grid must be strictly increasing")

    norm = float(np.linalg.norm(response))
    if norm <= 0.0:
        raise ResultValidationError("raw_A_TLS has zero norm and cannot define a normalized shape")
    expected_shape = response / norm
    normalized_shape = _as_finite_vector(record, "normalized_shape")
    if normalized_shape.shape != response.shape:
        raise ResultValidationError("normalized_shape and raw_A_TLS must have the same length")
    if not np.allclose(normalized_shape, expected_shape, rtol=1e-11, atol=1e-13):
        raise ResultValidationError("normalized_shape is inconsistent with raw_A_TLS")

    observed_weight = float(np.trapezoid(response**2, ratios))
    stored_weight = record.get("W_r")
    if not isinstance(stored_weight, (int, float)) or not np.isfinite(stored_weight):
        raise ResultValidationError("W_r must be a finite scalar")
    if not np.isclose(float(stored_weight), observed_weight, rtol=1e-11, atol=1e-13):
        raise ResultValidationError("W_r is inconsistent with raw_A_TLS and the detuning grid")

    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        raise ResultValidationError("Result provenance must be a JSON object")
    if expected_protocol_sha256 is not None and provenance.get("protocol_sha256") != expected_protocol_sha256:
        raise ResultValidationError("Result protocol hash does not match the frozen protocol")
    for key in ("protocol_sha256", "script_sha256", "git_commit", "command"):
        if key not in provenance:
            raise ResultValidationError(f"Result provenance is missing {key}")

    if require_self_hash:
        observed_hash = record.get("result_sha256_excluding_self")
        if not isinstance(observed_hash, str):
            raise ResultValidationError("Result is missing result_sha256_excluding_self")
        hash_payload = dict(record)
        hash_payload.pop("result_sha256_excluding_self", None)
        if canonical_sha256(hash_payload) != observed_hash:
            raise ResultValidationError("Result self hash does not match canonical payload")

    return {
        "points": float(response.size),
        "response_norm": norm,
        "spectral_weight": observed_weight,
        "peak_response": float(np.max(response)),
    }


def normalized_shape_distance(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
    """Compute a validated Euclidean distance between normalized TLS spectra."""
    validate_matching_grids(left, right)
    x = result_response(left)
    y = result_response(right)
    return float(np.linalg.norm(x / np.linalg.norm(x) - y / np.linalg.norm(y)))


def spectral_weight(record: Mapping[str, Any]) -> float:
    """Return a validated ratio-grid spectral weight."""
    ratios = result_ratios(record)
    response = result_response(record)
    return float(np.trapezoid(response**2, ratios))

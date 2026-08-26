#!/usr/bin/env python3
"""Validate committed Gate A v3 results and optionally generate deterministic audit figures.

The default output location is outside versioned result data.  Use ``--check-only``
in continuous integration or reviewer verification when no derived files should be
written.  The script never launches an expensive Floquet--Lindblad calculation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from result_validation import (
    ResultValidationError,
    normalized_shape_distance,
    result_ratios,
    result_response,
    spectral_weight,
    validate_matching_grids,
    validate_result_record,
)

REPO = Path(__file__).resolve().parents[2]
DEFAULT_V3 = REPO / "results/gate_a_v3/gate_a_v3.0__1b3dd5130c77"
DEFAULT_V2 = REPO / "results/gate_a_v2/gate_a_v2.0__00d3477cc81e"
DEFAULT_OUTPUT = REPO / "build/gate_a_v3_audit"

# Fix both text and math fonts for minimal reviewer/CI environments.  ASCII
# hyphens prevent a missing Unicode-minus glyph from contaminating audit logs.
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "mathtext.fontset": "dejavusans",
        "axes.unicode_minus": False,
    }
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metric(numerator: dict, denominator: dict) -> dict[str, float]:
    grid = validate_matching_grids(numerator, denominator)
    x = result_response(numerator)
    y = result_response(denominator)
    denominator_weight = float(np.trapezoid(y**2, grid))
    if denominator_weight <= 0.0 or float(np.max(y)) <= 0.0:
        raise ResultValidationError("Cannot form a directional ratio with a zero denominator spectrum")
    return {
        "W_numerator": spectral_weight(numerator),
        "W_denominator": denominator_weight,
        "directional_W_ratio": spectral_weight(numerator) / denominator_weight,
        "shape_distance": normalized_shape_distance(numerator, denominator),
        "raw_peak_ratio": float(np.max(x) / np.max(y)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v3-dir", type=Path, default=DEFAULT_V3, help="Versioned Gate A v3 result directory")
    parser.add_argument("--v2-dir", type=Path, default=DEFAULT_V2, help="Versioned Gate A v2 baseline directory")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Directory for derived audit JSON and figures")
    parser.add_argument("--check-only", action="store_true", help="Validate committed records and print the audit without writing outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    v3 = args.v3_dir.resolve()
    v2 = args.v2_dir.resolve()
    manifest = load(v3 / "MANIFEST.json")
    protocol_sha = manifest.get("protocol_sha256")
    if not isinstance(protocol_sha, str):
        raise SystemExit("Manifest is missing protocol_sha256")

    manifest_checks = {
        path: {"expected": expected, "actual": sha(REPO / path), "matches": sha(REPO / path) == expected}
        for path, expected in manifest["sha256"].items()
    }
    if not all(item["matches"] for item in manifest_checks.values()):
        raise SystemExit("Gate A v3 manifest hash mismatch")

    records = {
        "nu11": load(v2 / "primary_controls/topological_obc_production_v2__m0.json"),
        "nu01": load(v3 / "nu01_OBC_m0.json"),
        "nu10": load(v3 / "nu10_OBC_m0.json"),
        "nu00": load(v3 / "nu00_OBC_m0.json"),
        "heldout_obc": load(v2 / "heldout_controls/heldout_topological_obc_v2__m0.json"),
        "heldout_pbc": load(v3 / "heldout_PBC_m0.json"),
    }
    for label in ("nu01", "nu10", "nu00", "heldout_pbc"):
        validate_result_record(records[label], expected_protocol_sha256=protocol_sha)
    for label in ("nu11", "heldout_obc"):
        if not np.all(np.isfinite(result_response(records[label]))):
            raise SystemExit(f"Invalid v2 baseline response: {label}")

    pairs = {
        "nu11_over_nu01": metric(records["nu11"], records["nu01"]),
        "nu10_over_nu00": metric(records["nu10"], records["nu00"]),
        "heldout_OBC_over_PBC": metric(records["heldout_obc"], records["heldout_pbc"]),
    }
    spatial = {0: records["nu11"]}
    spatial.update({m: load(v3 / f"production_spatial_m{m}.json") for m in range(1, 6)})
    for m in range(1, 6):
        validate_result_record(spatial[m], expected_protocol_sha256=protocol_sha)
    spatial_weights = {str(m): spectral_weight(record) for m, record in spatial.items()}
    spatial_ratios = {f"W_m0_over_m{m}": spatial_weights["0"] / spatial_weights[str(m)] for m in range(1, 6)}

    convergence = {"baseline_s4_d20_v2": records["nu11"]}
    for tag in ("convergence_s2_d20", "convergence_s8_d20", "convergence_s4_d8", "convergence_s4_d40"):
        convergence[tag] = load(v3 / f"{tag}.json")
        validate_result_record(convergence[tag], expected_protocol_sha256=protocol_sha)
    convergence_metrics = {
        tag: {
            "shape_distance_to_baseline": normalized_shape_distance(record, records["nu11"]),
            "raw_peak_ratio_to_baseline": float(np.max(result_response(record)) / np.max(result_response(records["nu11"]))),
            "W_ratio_to_baseline": spectral_weight(record) / spectral_weight(records["nu11"]),
        }
        for tag, record in convergence.items()
        if tag != "baseline_s4_d20_v2"
    }

    d11_01 = normalized_shape_distance(records["nu11"], records["nu01"])
    d10_00 = normalized_shape_distance(records["nu10"], records["nu00"])
    cross = [
        normalized_shape_distance(left, right)
        for left in (records["nu11"], records["nu01"])
        for right in (records["nu10"], records["nu00"])
    ]
    pi_pattern = {
        "within_nupi1_D": d11_01,
        "within_nupi0_D": d10_00,
        "cross_nupi_D_values": cross,
        "cross_nupi_min": min(cross),
        "qualitative_support_for_pi_grouping": bool(d11_01 < min(cross)),
        "frozen_interpretation": "The prospectively frozen normalized-lineshape grouping criterion fails. This rules out a universal nu_pi-determined spectral-shape claim for this data set.",
        "note": "A failed lineshape grouping does not imply that nu_pi is physically irrelevant to every response metric.",
    }
    weights = {label: spectral_weight(records[label]) for label in ("nu11", "nu01", "nu10", "nu00")}
    weight_stratification = {
        "status": "exploratory_descriptive_not_a_frozen_pass_fail_test",
        "W_r_by_BDI_label": weights,
        "nu11_over_nu10": weights["nu11"] / weights["nu10"],
        "nu01_over_nu00": weights["nu01"] / weights["nu00"],
        "min_nupi1_over_max_nupi0": min(weights["nu11"], weights["nu01"]) / max(weights["nu10"], weights["nu00"]),
        "interpretation": "Across the four sampled drives, both nupi=1 raw integrated weights exceed both nupi=0 weights. The nupi sectors lie on different equal-period control lines, so this amplitude separation is exploratory.",
    }
    payload = {
        "schema": "gate_a_v3_audit_v3",
        "v3_manifest_sha256": sha(v3 / "MANIFEST.json"),
        "v3_integrity": manifest_checks,
        "source_sha256": {
            "nu11_v2": sha(v2 / "primary_controls/topological_obc_production_v2__m0.json"),
            "heldout_obc_v2": sha(v2 / "heldout_controls/heldout_topological_obc_v2__m0.json"),
        },
        "directional_pairs": pairs,
        "spatial_W_r": spatial_weights,
        "spatial_directional_ratios": spatial_ratios,
        "convergence": convergence_metrics,
        "pi_pattern": pi_pattern,
        "exploratory_weight_stratification": weight_stratification,
        "protocol_interpretation": "All directional ratios use the declared numerator/denominator order. V3 resolves the unequal-period v2 trivial control, but has no single common-period line containing all four BDI classes.",
    }
    print(json.dumps(payload, indent=2))
    if args.check_only:
        return

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "GATE_A_V3_AUDIT.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.6), constrained_layout=True)
    panels = [
        (axes[0, 0], [(records["nu11"], "(1,1) OBC"), (records["nu01"], "(0,1) OBC")], r"matched $T$: $(1,1)$ vs $(0,1)$"),
        (axes[0, 1], [(records["nu10"], "(1,0) OBC"), (records["nu00"], "(0,0) OBC")], r"matched $T$: $(1,0)$ vs $(0,0)$"),
        (axes[1, 1], [(records["heldout_obc"], "held-out (1,1) OBC"), (records["heldout_pbc"], "held-out same-drive PBC")], "held-out boundary control"),
    ]
    for axis, items, title in panels:
        for record, label in items:
            axis.plot(result_ratios(record), result_response(record), marker="o", ms=3, label=label)
        axis.axvline(1.0, color=".5", ls=":", lw=0.8)
        axis.set(title=title, xlabel=r"$\omega_d/(\Omega/2)$", ylabel=r"raw $A_{TLS}$")
        axis.grid(alpha=0.25)
        axis.legend(fontsize=8)
    axes[1, 0].plot(list(range(6)), [spatial_weights[str(m)] for m in range(6)], marker="o", color="black")
    axes[1, 0].set(title="production OBC spatial profile", xlabel="TLS contact site m", ylabel=r"$W_r(m)$")
    axes[1, 0].grid(alpha=0.25)
    fig.savefig(output / "GATE_A_V3_CONTROLS.png", dpi=260)
    fig.savefig(output / "GATE_A_V3_CONTROLS.pdf")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(6.8, 3.8))
    tags = list(convergence_metrics)
    values = [convergence_metrics[tag]["shape_distance_to_baseline"] for tag in tags]
    axis.bar(range(len(tags)), values, color=["#0072b2", "#009e73", "#d55e00", "#cc79a7"])
    axis.axhline(0.10, color="black", ls="--", label="frozen acceptance 0.10")
    axis.set(xticks=range(len(tags)), xticklabels=["s2,d20", "s8,d20", "s4,d8", "s4,d40"], ylabel="normalized-shape distance", title="production numerical convergence")
    axis.legend()
    fig.tight_layout()
    fig.savefig(output / "GATE_A_V3_CONVERGENCE.png", dpi=260)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(6.8, 3.8))
    labels = ["(1,1)", "(0,1)", "(1,0)", "(0,0)"]
    colors = ["#0072b2", "#009e73", "#d55e00", "#cc79a7"]
    axis.bar(range(4), [weights["nu11"], weights["nu01"], weights["nu10"], weights["nu00"]], color=colors)
    axis.set(xticks=range(4), xticklabels=labels, yscale="log", ylabel=r"raw $W_r$", title="exploratory raw-weight separation by sampled BDI label")
    axis.text(0.5, 0.95, r"Not a frozen $\nu_\pi$ pass/fail test", transform=axis.transAxes, ha="center", va="top", fontsize=9)
    fig.tight_layout()
    fig.savefig(output / "GATE_A_V3_WEIGHT_STRATIFICATION.png", dpi=260)
    plt.close(fig)


if __name__ == "__main__":
    main()

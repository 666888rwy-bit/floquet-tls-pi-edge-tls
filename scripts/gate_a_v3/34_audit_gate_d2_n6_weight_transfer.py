#!/usr/bin/env python3
"""Read-only-by-default audit of the complete frozen Gate D2 campaign."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from gate_d2_validation import (
    ResultValidationError,
    canonical_sha256,
    load_json,
    sha256_path,
    validate_authorization,
    validate_gate_d2_result,
)

REPO = Path(__file__).resolve().parents[2]
PROTOCOL = REPO / "protocols/gate_d2/gate_d2_n6_nupi_weight_transfer_protocol.json"
RUNNER = REPO / "scripts/gate_a_v3/33_run_gate_d2_n6_weight_transfer.py"
HELPER = REPO / "scripts/gate_a_v2/10_full_model_common_preparation.py"
N4_ROOT = REPO / "results/gate_d1/gate_d1.0__6d3a08047527"


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def validate_n4_record(record: dict, *, task: dict, protocol: dict, expected_file_sha: str, path: Path) -> dict:
    if sha256_path(path) != expected_file_sha:
        raise ResultValidationError(f"Gate D1 manifest file hash mismatch: {task['id']}")
    if record.get("schema") != "gate_d1_n4_full_model_result_v1":
        raise ResultValidationError(f"Unexpected Gate D1 result schema: {task['id']}")
    if record.get("task") != task:
        raise ResultValidationError(f"Gate D1 task drift: {task['id']}")
    payload = dict(record)
    observed_self_hash = payload.pop("result_sha256_excluding_self", None)
    if canonical_sha256(payload) != observed_self_hash:
        raise ResultValidationError(f"Gate D1 result self hash mismatch: {task['id']}")
    expected_protocol_sha = sha256_path(
        REPO / protocol["authorization"]["source_gate_d1_protocol"]
    )
    if record.get("provenance", {}).get("protocol_sha256") != expected_protocol_sha:
        raise ResultValidationError(f"Gate D1 protocol provenance mismatch: {task['id']}")

    ratios = np.asarray(record.get("ratios"), dtype=float)
    raw = np.asarray(record.get("raw_A_TLS"), dtype=float)
    normalized = np.asarray(record.get("normalized_shape"), dtype=float)
    frozen_ratios = np.asarray(
        protocol["common_physical_protocol"][
            "detuning_ratios_omega_d_over_Omega_over_2"
        ],
        dtype=float,
    )
    if any(vector.ndim != 1 for vector in (ratios, raw, normalized)):
        raise ResultValidationError(f"Gate D1 arrays are not one-dimensional: {task['id']}")
    if not (ratios.shape == raw.shape == normalized.shape == frozen_ratios.shape):
        raise ResultValidationError(f"Gate D1 array lengths differ: {task['id']}")
    if not all(np.all(np.isfinite(vector)) for vector in (ratios, raw, normalized)):
        raise ResultValidationError(f"Gate D1 arrays contain non-finite values: {task['id']}")
    if not np.array_equal(ratios, frozen_ratios):
        raise ResultValidationError(f"Gate D1 and Gate D2 ratio grids differ: {task['id']}")
    if np.any(raw < 0.0) or not np.all(np.diff(ratios) > 0.0):
        raise ResultValidationError(f"Gate D1 response/grid constraints fail: {task['id']}")
    norm = float(np.linalg.norm(raw))
    if norm <= 0.0 or not np.allclose(normalized, raw / norm, rtol=1e-11, atol=1e-13):
        raise ResultValidationError(f"Gate D1 normalized_shape definition mismatch: {task['id']}")
    weight = float(np.trapezoid(raw**2, ratios))
    if not np.isclose(float(record["W_r"]), weight, rtol=1e-11, atol=1e-13):
        raise ResultValidationError(f"Gate D1 W_r mismatch: {task['id']}")
    return {"ratios": ratios, "raw": raw, "weight": weight}


def build_audit() -> tuple[dict, dict]:
    protocol = load_json(PROTOCOL)
    authorization = validate_authorization(protocol=protocol, repository=REPO)
    protocol_sha = sha256_path(PROTOCOL)
    runner_sha = sha256_path(RUNNER)
    helper_sha = sha256_path(HELPER)
    campaign_root = REPO / "results/gate_d2" / f"{protocol['protocol_version']}__{protocol_sha[:12]}"
    manifest_path = campaign_root / "MANIFEST.json"
    if not manifest_path.exists():
        raise ResultValidationError(
            "Gate D2 is incomplete: MANIFEST.json is absent; resume the local campaign first"
        )
    manifest = load_json(manifest_path)
    if manifest.get("schema") != "gate_d2_final_manifest_v2":
        raise ResultValidationError("Unexpected Gate D2 final manifest schema")
    if manifest.get("protocol_sha256") != protocol_sha:
        raise ResultValidationError("Gate D2 manifest protocol hash mismatch")
    if manifest.get("script_sha256") != runner_sha:
        raise ResultValidationError("Gate D2 manifest runner hash differs from current frozen runner")
    if manifest.get("helper_sha256") != helper_sha:
        raise ResultValidationError("Gate D2 manifest helper hash differs from current helper")
    manifest_commit = manifest.get("git_commit")
    if not isinstance(manifest_commit, str) or len(manifest_commit) != 40:
        raise ResultValidationError("Gate D2 manifest lacks a full freeze commit")
    if manifest.get("authorization") != authorization:
        raise ResultValidationError("Gate D2 manifest authorization record mismatch")

    tasks = protocol["selected_drives"]
    expected_ids = [task["id"] for task in tasks]
    result_files = manifest.get("result_files")
    if not isinstance(result_files, dict) or set(result_files) != set(expected_ids):
        raise ResultValidationError("Manifest does not contain exactly the eight frozen drive IDs")

    n4_manifest = load_json(N4_ROOT / "MANIFEST.json")
    if n4_manifest.get("protocol_sha256") != authorization["source_gate_d1_protocol_sha256"]:
        raise ResultValidationError("Gate D1 manifest protocol hash mismatch")
    n4_paths = {Path(path).stem: path for path in n4_manifest.get("results", [])}
    if set(n4_paths) != set(expected_ids):
        raise ResultValidationError("Gate D1 manifest does not contain the same eight drives")

    records: list[dict] = []
    integrity: dict[str, dict] = {}
    for task in tasks:
        drive_id = task["id"]
        entry = result_files[drive_id]
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ResultValidationError(f"Malformed Gate D2 manifest entry: {drive_id}")
        n6_path = (REPO / entry["path"]).resolve()
        if not n6_path.is_relative_to(campaign_root.resolve()):
            raise ResultValidationError(f"Gate D2 result path escapes campaign root: {drive_id}")
        if sha256_path(n6_path) != entry.get("sha256"):
            raise ResultValidationError(f"Gate D2 manifest file hash mismatch: {drive_id}")
        if entry.get("git_commit") != manifest_commit:
            raise ResultValidationError(f"Gate D2 manifest mixes freeze commits: {drive_id}")
        n6 = load_json(n6_path)
        n6_diagnostics = validate_gate_d2_result(
            n6,
            expected_task=task,
            protocol=protocol,
            protocol_sha256=protocol_sha,
            runner_sha256=runner_sha,
            helper_sha256=helper_sha,
            expected_git_commit=manifest_commit,
        )

        n4_relative = n4_paths[drive_id]
        n4_path = REPO / n4_relative
        n4 = load_json(n4_path)
        n4_data = validate_n4_record(
            n4,
            task=task,
            protocol=protocol,
            expected_file_sha=n4_manifest["sha256"][n4_relative],
            path=n4_path,
        )
        n6_ratios = np.asarray(n6["ratios"], dtype=float)
        n6_raw = np.asarray(n6["raw_A_TLS"], dtype=float)
        if not np.array_equal(n4_data["ratios"], n6_ratios):
            raise ResultValidationError(f"N4/N6 ratio grid mismatch: {drive_id}")
        shape_distance = float(
            np.linalg.norm(
                n4_data["raw"] / np.linalg.norm(n4_data["raw"])
                - n6_raw / np.linalg.norm(n6_raw)
            )
        )
        records.append(
            {
                "id": drive_id,
                "nu0": task["nu0"],
                "nupi": task["nupi"],
                "alpha_over_pi": task["alpha_over_pi"],
                "beta_over_pi": task["beta_over_pi"],
                "W_r_N4": n4_data["weight"],
                "W_r_N6": n6_diagnostics["spectral_weight"],
                "N6_over_N4": n6_diagnostics["spectral_weight"] / n4_data["weight"],
                "N4_N6_shape_distance": shape_distance,
                "raw_peak_N6": n6_diagnostics["peak_response"],
                "grid_peak_ratio_N6": float(n6_ratios[int(np.argmax(n6_raw))]),
            }
        )
        integrity[drive_id] = {
            "manifest_file_sha256": True,
            "result_schema_and_self_hash": True,
            "runner_and_helper_sha256": True,
            "task_fieldwise_match": True,
            "N4_N6_ratio_grid_exact_match": True,
            "normalized_shape_definition": True,
            "W_r_recomputed": True,
        }

    groups = {
        (nu0, nupi): [
            row["W_r_N6"] for row in records
            if row["nu0"] == nu0 and row["nupi"] == nupi
        ]
        for nu0 in (0, 1) for nupi in (0, 1)
    }
    medians = {
        f"nu{nu0}{nupi}": float(np.median(groups[(nu0, nupi)]))
        for nu0 in (0, 1) for nupi in (0, 1)
    }
    ratio_nu0_0 = medians["nu01"] / medians["nu00"]
    ratio_nu0_1 = medians["nu11"] / medians["nu10"]
    all_point_ratio = min(groups[(0, 1)] + groups[(1, 1)]) / max(
        groups[(0, 0)] + groups[(1, 0)]
    )
    decision = {
        "nu0_0_median_ratio": ratio_nu0_0,
        "nu0_1_median_ratio": ratio_nu0_1,
        "min_nupi1_over_max_nupi0": all_point_ratio,
        "condition_1_both_fixed_nu0_median_ratios_gt_10": bool(
            ratio_nu0_0 > 10 and ratio_nu0_1 > 10
        ),
        "condition_2_all_nupi1_weights_exceed_all_nupi0": bool(all_point_ratio > 1),
    }
    decision["gate_d2_pass"] = bool(
        decision["condition_1_both_fixed_nu0_median_ratios_gt_10"]
        and decision["condition_2_all_nupi1_weights_exceed_all_nupi0"]
    )
    log_n4 = np.log10([row["W_r_N4"] for row in records])
    log_n6 = np.log10([row["W_r_N6"] for row in records])
    payload = {
        "schema": "gate_d2_n6_weight_transfer_audit_v2",
        "protocol_sha256": protocol_sha,
        "manifest_sha256": sha256_path(manifest_path),
        "runner_sha256": runner_sha,
        "helper_sha256": helper_sha,
        "authorization": authorization,
        "integrity": integrity,
        "records": records,
        "class_median_W_r_N6": medians,
        "frozen_confirmation": decision,
        "secondary_size_transfer": {
            "log10_weight_Pearson_correlation_N4_N6": float(
                np.corrcoef(log_n4, log_n6)[0, 1]
            ),
            "median_N6_over_N4": float(
                np.median([row["N6_over_N4"] for row in records])
            ),
        },
        "interpretation_boundary": protocol["predeclared_analysis"][
            "interpretation_if_successful"
            if decision["gate_d2_pass"] else "interpretation_if_failed"
        ],
        "prohibited_inference": (
            "Gate D2 cannot establish a common-period causal law, a thermodynamic "
            "topological invariant, universal pi-edge spectroscopy, or a universal lineshape."
        ),
    }
    context = {"records": records, "campaign_root": campaign_root}
    return payload, context


def write_figure(records: list[dict], destination: Path) -> None:
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(5.2, 4.5))
    colors = {0: "#d55e00", 1: "#0072b2"}
    markers = {0: "s", 1: "o"}
    for row in records:
        axis.scatter(
            row["W_r_N4"],
            row["W_r_N6"],
            color=colors[row["nupi"]],
            marker=markers[row["nu0"]],
            s=70,
            label=rf"$\nu_0={row['nu0']},\nu_\pi={row['nupi']}$",
        )
        axis.annotate(row["id"], (row["W_r_N4"], row["W_r_N6"]), fontsize=7)
    low = min(min(row["W_r_N4"] for row in records), min(row["W_r_N6"] for row in records))
    high = max(max(row["W_r_N4"] for row in records), max(row["W_r_N6"] for row in records))
    axis.plot([low, high], [low, high], color="0.5", linestyle="--", linewidth=0.9)
    axis.set(
        xscale="log",
        yscale="log",
        xlabel=r"$N=4$ raw integrated weight $W_r$",
        ylabel=r"$N=6$ raw integrated weight $W_r$",
        title="Gate D2: frozen finite-size transfer test",
    )
    handles, labels = axis.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    axis.legend(unique.values(), unique.keys(), fontsize=8, ncol=2)
    axis.grid(alpha=0.25, which="both")
    figure.tight_layout()
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=260)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate and report without creating any derived files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("build/gate_d2_audit"),
        help="derived-output directory; defaults outside versioned results",
    )
    args = parser.parse_args()
    try:
        payload, context = build_audit()
    except (OSError, ValueError, KeyError, TypeError, ResultValidationError) as exc:
        raise SystemExit(f"Gate D2 audit failed: {exc}") from exc
    print(json.dumps({"frozen_confirmation": payload["frozen_confirmation"]}, indent=2))
    if args.check_only:
        return
    output_dir = args.output_dir if args.output_dir.is_absolute() else REPO / args.output_dir
    atomic_json(output_dir / "GATE_D2_N6_WEIGHT_TRANSFER_AUDIT.json", payload)
    write_figure(context["records"], output_dir / "GATE_D2_N4_N6_WEIGHT_TRANSFER.png")
    print(f"Derived audit outputs written to {output_dir}")


if __name__ == "__main__":
    main()

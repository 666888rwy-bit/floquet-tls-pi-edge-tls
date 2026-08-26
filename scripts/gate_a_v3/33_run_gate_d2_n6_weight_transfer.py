#!/usr/bin/env python3
"""Exact N=6 Gate D2 weight-transfer campaign with strict safe resume."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from gate_d2_validation import (
    ResultValidationError,
    canonical_sha256,
    load_json,
    runtime_environment,
    sha256_path,
    validate_authorization,
    validate_gate_d2_result,
)

REPO = Path(__file__).resolve().parents[2]
PROTOCOL = REPO / "protocols/gate_d2/gate_d2_n6_nupi_weight_transfer_protocol.json"
HELPER = REPO / "scripts/gate_a_v2/10_full_model_common_preparation.py"
OUTROOT = REPO / "results/gate_d2"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def git_stdout(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def load_helper():
    spec = importlib.util.spec_from_file_location("gate_d2_full_model", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load full-model helper: {HELPER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["gate_d2_full_model"] = module
    spec.loader.exec_module(module)
    return module


def public_commit_refs(commit: str) -> list[str]:
    """Require the exact running commit to exist on the configured public remote."""
    try:
        output = git_stdout("ls-remote", "origin")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "Cannot verify the required public freeze commit. Check network access and origin, then retry."
        ) from exc
    refs = []
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[0] == commit:
            refs.append(fields[1])
    if not refs:
        raise SystemExit(
            "Refusing propagation: the current clean commit is not present on origin. "
            "Commit and push the Gate D2 freeze source first."
        )
    return sorted(refs)


def clean_for_run(output_dir: Path, resume: bool) -> None:
    lines = git_stdout("status", "--porcelain", "--untracked-files=all").splitlines()
    allowed_prefix = str(output_dir.relative_to(REPO)) + "/"
    disallowed = [
        line for line in lines
        if not (resume and len(line) >= 4 and line[3:].startswith(allowed_prefix))
    ]
    if disallowed:
        raise SystemExit(
            "Refusing a dirty worktree. Commit the frozen Gate D2 source first; "
            "--resume permits changes only inside this campaign output directory.\n"
            + "\n".join(disallowed)
        )


def validate_existing(
    path: Path,
    *,
    task: dict,
    protocol: dict,
    protocol_sha: str,
    runner_sha: str,
    helper_sha: str,
    git_commit: str,
) -> tuple[bool, str | None, dict | None]:
    try:
        record = load_json(path)
        validate_gate_d2_result(
            record,
            expected_task=task,
            protocol=protocol,
            protocol_sha256=protocol_sha,
            runner_sha256=runner_sha,
            helper_sha256=helper_sha,
            expected_git_commit=git_commit,
        )
        return True, None, record
    except (OSError, ValueError, KeyError, TypeError, ResultValidationError) as exc:
        return False, f"{type(exc).__name__}: {exc}", None


def checkpoint_manifest(
    output_dir: Path,
    *,
    protocol: dict,
    protocol_sha: str,
    runner_sha: str,
    helper_sha: str,
    git_commit: str,
    authorization: dict,
) -> dict:
    valid: dict[str, dict] = {}
    invalid: dict[str, str] = {}
    missing: list[str] = []
    for task in protocol["selected_drives"]:
        path = output_dir / f"{task['id']}.json"
        if not path.exists():
            missing.append(task["id"])
            continue
        ok, error, record = validate_existing(
            path,
            task=task,
            protocol=protocol,
            protocol_sha=protocol_sha,
            runner_sha=runner_sha,
            helper_sha=helper_sha,
            git_commit=git_commit,
        )
        if ok and record is not None:
            valid[task["id"]] = {
                "path": str(path.relative_to(REPO)),
                "sha256": sha256_path(path),
                "git_commit": record["provenance"]["git_commit"],
            }
        else:
            invalid[task["id"]] = error or "unknown validation failure"
    manifest = {
        "schema": "gate_d2_checkpoint_manifest_v2",
        "protocol_sha256": protocol_sha,
        "script_sha256": runner_sha,
        "helper_sha256": helper_sha,
        "git_commit": git_commit,
        "authorization": authorization,
        "valid_completed": valid,
        "missing": missing,
        "invalid": invalid,
        "updated_utc": utc_now(),
    }
    atomic_json(output_dir / "CHECKPOINT_MANIFEST.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drive", action="append", default=[], help="repeatable frozen drive ID")
    parser.add_argument("--dry-run", action="store_true", help="validate anchors and list work only")
    parser.add_argument("--resume", action="store_true", help="reuse only fully validated result files")
    args = parser.parse_args()

    protocol = load_json(PROTOCOL)
    if protocol.get("status") != "prospectively_frozen_public_commit_required_before_run":
        raise SystemExit("Unexpected Gate D2 protocol status.")
    try:
        authorization = validate_authorization(protocol=protocol, repository=REPO)
    except ResultValidationError as exc:
        raise SystemExit(f"Gate D2 authorization failed before propagation: {exc}") from exc

    protocol_sha = sha256_path(PROTOCOL)
    runner_sha = sha256_path(Path(__file__))
    helper_sha = sha256_path(HELPER)
    commit = git_stdout("rev-parse", "HEAD")
    output_dir = OUTROOT / f"{protocol['protocol_version']}__{protocol_sha[:12]}"
    allowed_ids = [task["id"] for task in protocol["selected_drives"]]
    unknown = sorted(set(args.drive) - set(allowed_ids))
    if unknown:
        raise SystemExit(f"Unknown frozen drive ID(s): {unknown}")
    requested = [
        task for task in protocol["selected_drives"]
        if not args.drive or task["id"] in args.drive
    ]

    completed: list[str] = []
    pending: list[dict] = []
    invalid: list[dict] = []
    for task in requested:
        path = output_dir / f"{task['id']}.json"
        if not path.exists():
            pending.append(task)
            continue
        ok, error, _ = validate_existing(
            path,
            task=task,
            protocol=protocol,
            protocol_sha=protocol_sha,
            runner_sha=runner_sha,
            helper_sha=helper_sha,
            git_commit=commit,
        )
        if ok:
            completed.append(task["id"])
        else:
            invalid.append({"id": task["id"], "error": error})

    plan = {
        "protocol_sha256": protocol_sha,
        "authorization": authorization,
        "output_dir": str(output_dir.relative_to(REPO)),
        "requested": [task["id"] for task in requested],
        "skipped_valid": completed,
        "pending": [task["id"] for task in pending],
        "invalid_existing": invalid,
        "execution_note": "The full N=6 campaign exceeds five minutes and is intentionally local-only.",
    }
    print(json.dumps(plan, indent=2))
    if args.dry_run:
        return
    if invalid:
        raise SystemExit("Refusing to overwrite invalid or provenance-incompatible results.")

    clean_for_run(output_dir, args.resume)
    remote_refs = public_commit_refs(commit)
    if output_dir.exists() and pending and not args.resume:
        raise SystemExit("Output directory exists. Inspect it, then rerun with --resume.")
    if not pending:
        print("All requested Gate D2 drives are complete and valid.")
        return

    full = load_helper()
    common = protocol["common_physical_protocol"]
    ratios = np.asarray(common["detuning_ratios_omega_d_over_Omega_over_2"], dtype=float)
    environment = runtime_environment()
    repository_url = git_stdout("config", "--get", "remote.origin.url")
    output_dir.mkdir(parents=True, exist_ok=True)

    for task in pending:
        timing = full.make_timing(
            task["alpha_over_pi"], task["beta_over_pi"], common["J"], common["h"]
        )
        if not np.isclose(task["T"], timing.period, rtol=0.0, atol=1e-12):
            raise SystemExit(f"Timing mismatch for {task['id']}")
        if not np.isclose(task["Omega"], timing.omega, rtol=0.0, atol=1e-12):
            raise SystemExit(f"Omega mismatch for {task['id']}")
        coupling = common["gT_target"] / timing.period
        damping = common["gamma1T_target"] / timing.period
        system = full.build_system(
            n_chain=common["N_chain"],
            jcoupling=common["J"],
            hfield=common["h"],
            boundary=common["boundary"],
            contact=common["TLS_contact_site"],
            gamma1=damping,
        )
        started = utc_now()
        values: list[float] = []
        for number, ratio in enumerate(ratios, 1):
            value = full.response_at_ratio(
                system,
                timing,
                ratio=float(ratio),
                g=coupling,
                periods=common["periods"],
                samples_per_half=common["samples_per_half_step"],
                discard_periods=common["discard_periods"],
            )
            values.append(value)
            print(
                f"[{task['id']}] {number}/{len(ratios)} r={ratio:.3f} A={value:.9g}",
                flush=True,
            )
        raw = np.asarray(values, dtype=float)
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
                "T": timing.period,
                "Omega": timing.omega,
                "g": coupling,
                "gamma1": damping,
                "gT": coupling * timing.period,
                "gamma1T": damping * timing.period,
                "total_time": common["periods"] * timing.period,
            },
            "ratios": ratios.tolist(),
            "raw_A_TLS": raw.tolist(),
            "normalized_shape": (raw / float(np.linalg.norm(raw))).tolist(),
            "W_r": float(np.trapezoid(raw**2, ratios)),
            "provenance": {
                "protocol_sha256": protocol_sha,
                "script_sha256": runner_sha,
                "helper_sha256": helper_sha,
                "repository_url": repository_url,
                "git_commit": commit,
                "public_commit_refs": remote_refs,
                "run_started_utc": started,
                "run_finished_utc": utc_now(),
                "command": [
                    sys.executable,
                    str(Path(__file__).relative_to(REPO)),
                    *sys.argv[1:],
                ],
                "environment": environment,
            },
        }
        record["result_sha256_excluding_self"] = canonical_sha256(record)
        validate_gate_d2_result(
            record,
            expected_task=task,
            protocol=protocol,
            protocol_sha256=protocol_sha,
            runner_sha256=runner_sha,
            helper_sha256=helper_sha,
            expected_git_commit=commit,
        )
        atomic_json(output_dir / f"{task['id']}.json", record)
        checkpoint_manifest(
            output_dir,
            protocol=protocol,
            protocol_sha=protocol_sha,
            runner_sha=runner_sha,
            helper_sha=helper_sha,
            git_commit=commit,
            authorization=authorization,
        )

    checkpoint = checkpoint_manifest(
        output_dir,
        protocol=protocol,
        protocol_sha=protocol_sha,
        runner_sha=runner_sha,
        helper_sha=helper_sha,
        git_commit=commit,
        authorization=authorization,
    )
    if checkpoint["invalid"]:
        raise SystemExit("Gate D2 has invalid completed results; no final manifest was written.")
    if not checkpoint["missing"]:
        final_manifest = {
            "schema": "gate_d2_final_manifest_v2",
            "protocol_sha256": protocol_sha,
            "script_sha256": runner_sha,
            "helper_sha256": helper_sha,
            "git_commit": commit,
            "authorization": authorization,
            "result_files": checkpoint["valid_completed"],
            "created_utc": utc_now(),
        }
        atomic_json(output_dir / "MANIFEST.json", final_manifest)
        print("Gate D2 is complete; final manifest written.")
    else:
        print(f"Gate D2 checkpoint saved; remaining: {checkpoint['missing']}")


if __name__ == "__main__":
    main()

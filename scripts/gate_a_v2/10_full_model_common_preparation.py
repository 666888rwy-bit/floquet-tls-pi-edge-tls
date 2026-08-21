#!/usr/bin/env python3
"""Gate A v2 full-model topology controls with a common physical preparation.

This script deliberately performs **no Floquet diagonalization, pair selection,
B^(0) construction, or phase gauge fixing** in the full-response path.  Every
case begins from the same computational-basis product state

    |up_z>^{tensor N} tensor |0_d>,

and is propagated under the exact sparse piecewise Floquet--Lindblad model.
The protocol is read from ``protocols/gate_a_v2/gate_a_v2_protocol.json``.

Provenance policy
-----------------
The protocol and this script must be committed to the public repository before
an exact response is launched.  Each case/contact result records the protocol
and script SHA-256, Git commit, repository URL, executable command, UTC start
and finish time, and a canonical self-excluding result hash.

The default task runs only the three predeclared primary controls at m=0 and
m=3.  The held-out drive cannot be included accidentally.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import scipy
from scipy.sparse import csr_matrix, eye, kron
from scipy.sparse.linalg import expm_multiply

REPO = Path(__file__).resolve().parents[2]
PROTOCOL = REPO / "protocols/gate_a_v2/gate_a_v2_protocol.json"
RESULTS_ROOT = REPO / "results/gate_a_v2"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_canonical_without_field(payload: dict[str, Any], field: str) -> str:
    clone = dict(payload)
    clone.pop(field, None)
    encoded = json.dumps(clone, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def git_stdout(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def git_provenance() -> dict[str, str]:
    return {
        "repository_url": git_stdout("config", "--get", "remote.origin.url"),
        "git_commit": git_stdout("rev-parse", "HEAD"),
        "git_commit_short": git_stdout("rev-parse", "--short", "HEAD"),
        "git_status_before_run": git_stdout("status", "--porcelain"),
    }


def dense_to_sparse_operator(op: np.ndarray) -> csr_matrix:
    return csr_matrix(op.astype(complex))


def sparse_kron(factors: list[csr_matrix]) -> csr_matrix:
    out = csr_matrix([[1.0 + 0.0j]])
    for factor in factors:
        out = kron(out, factor, format="csr")
    return out


def site_operator(op: csr_matrix, site: int, nsites: int, identity: csr_matrix) -> csr_matrix:
    return sparse_kron([op if index == site else identity for index in range(nsites)])


def liouvillian(hamiltonian: csr_matrix, collapse: csr_matrix) -> csr_matrix:
    dim = hamiltonian.shape[0]
    identity = eye(dim, format="csr", dtype=complex)
    cdc = collapse.getH() @ collapse
    return (
        -1j * (kron(identity, hamiltonian, format="csr") - kron(hamiltonian.T, identity, format="csr"))
        + kron(collapse.conjugate(), collapse, format="csr")
        - 0.5 * kron(identity, cdc, format="csr")
        - 0.5 * kron(cdc.T, identity, format="csr")
    ).tocsr()


def expectation(op: csr_matrix, vectorized_rho: np.ndarray, dim: int) -> complex:
    return np.trace(op.toarray() @ vectorized_rho.reshape((dim, dim), order="F"))


def tls_phasor(times: np.ndarray, values: np.ndarray, discard_time: float, omega: float) -> float:
    mask = times >= discard_time
    selected_times = times[mask]
    selected_values = values[mask]
    if selected_times.size < 3:
        raise RuntimeError("The fixed phasor readout window has fewer than three samples.")
    centered = selected_values - selected_values.mean()
    phasor = 2.0 * np.trapezoid(centered * np.exp(1j * omega * selected_times / 2.0), selected_times)
    return float(abs(phasor / (selected_times[-1] - selected_times[0])))


@dataclass
class Timing:
    t1: float
    t2: float
    period: float
    omega: float
    omega_over_2: float


@dataclass
class FullSystem:
    hzz: csr_matrix
    hx: csr_matrix
    hd: csr_matrix
    hint: csr_matrix
    observable: csr_matrix
    collapse: csr_matrix
    rho_initial: np.ndarray
    dim: int


def build_system(*, n_chain: int, jcoupling: float, hfield: float, boundary: str, contact: int, gamma1: float) -> FullSystem:
    """Build a direct product-state full chain-TLS system; no Floquet basis appears here."""
    identity2 = dense_to_sparse_operator(np.eye(2, dtype=complex))
    x2 = dense_to_sparse_operator(np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex))
    z2 = dense_to_sparse_operator(np.diag([1.0, -1.0]).astype(complex))
    sm2 = dense_to_sparse_operator(np.array([[0.0, 1.0], [0.0, 0.0]], dtype=complex))
    total_sites = n_chain + 1
    dim = 2**total_sites
    zs = [site_operator(z2, site, total_sites, identity2) for site in range(total_sites)]
    xs = [site_operator(x2, site, total_sites, identity2) for site in range(total_sites)]
    sms = [site_operator(sm2, site, total_sites, identity2) for site in range(total_sites)]

    links = [(site, site + 1) for site in range(n_chain - 1)]
    if boundary == "PBC":
        links.append((n_chain - 1, 0))
    elif boundary != "OBC":
        raise ValueError(f"Unknown boundary condition: {boundary}")
    hzz = sum((-jcoupling * zs[left] @ zs[right] for left, right in links), start=csr_matrix((dim, dim), dtype=complex))
    hx = sum((-hfield * xs[site] for site in range(n_chain)), start=csr_matrix((dim, dim), dtype=complex))
    hd = -0.5 * zs[n_chain]
    hint = sms[contact].getH() @ sms[n_chain] + sms[contact] @ sms[n_chain].getH()
    observable = sms[n_chain]
    collapse = np.sqrt(gamma1) * sms[n_chain]

    # Computational order is chain sites 0...N-1 then TLS.  The all-zero bit
    # vector is exactly |up_z>^{tensor N} tensor |0_d>, independent of U_F.
    psi_initial = np.zeros(dim, dtype=complex)
    psi_initial[0] = 1.0
    rho_initial = np.outer(psi_initial, psi_initial.conj()).reshape(-1, order="F")
    return FullSystem(hzz, hx, hd, hint, observable, collapse, rho_initial, dim)


def response_at_ratio(
    system: FullSystem, timing: Timing, *, ratio: float, g: float, periods: int,
    samples_per_half: int, discard_periods: int,
) -> float:
    l1 = liouvillian(system.hzz + ratio * timing.omega_over_2 * system.hd + g * system.hint, system.collapse)
    l2 = liouvillian(system.hx + ratio * timing.omega_over_2 * system.hd + g * system.hint, system.collapse)
    state = system.rho_initial.copy()
    sample_times: list[float] = []
    sample_values: list[complex] = []
    current_time = 0.0
    for _period in range(periods):
        segment1 = expm_multiply(l1, state, start=0.0, stop=timing.t1, num=samples_per_half + 1, endpoint=True)
        for sample in range(samples_per_half):
            sample_times.append(current_time + sample * timing.t1 / samples_per_half)
            sample_values.append(expectation(system.observable, segment1[sample], system.dim))
        state = segment1[-1]
        current_time += timing.t1
        segment2 = expm_multiply(l2, state, start=0.0, stop=timing.t2, num=samples_per_half + 1, endpoint=True)
        for sample in range(samples_per_half):
            sample_times.append(current_time + sample * timing.t2 / samples_per_half)
            sample_values.append(expectation(system.observable, segment2[sample], system.dim))
        state = segment2[-1]
        current_time += timing.t2
    return tls_phasor(np.asarray(sample_times), np.asarray(sample_values), discard_periods * timing.period, timing.omega)


def make_timing(alpha_over_pi: float, beta_over_pi: float, jcoupling: float, hfield: float) -> Timing:
    alpha = alpha_over_pi * np.pi
    beta = beta_over_pi * np.pi
    t1 = beta / (2.0 * jcoupling)
    t2 = alpha / (2.0 * hfield)
    period = t1 + t2
    omega = 2.0 * np.pi / period
    return Timing(float(t1), float(t2), float(period), float(omega), float(omega / 2.0))


def code_environment() -> dict[str, str]:
    return {
        "python": sys.version.replace("\n", " "),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "matplotlib": matplotlib.__version__,
        "platform": platform.platform(),
    }


def run_one(case: dict[str, Any], contact: int, protocol: dict[str, Any], output_dir: Path, command: list[str]) -> Path:
    fixed = protocol["fixed_chain_TLS_model"]
    measurement = protocol["full_model_measurement_protocol"]
    run_start = utc_now()
    provenance = {
        **git_provenance(),
        "protocol_version": protocol["protocol_version"],
        "protocol_path": str(PROTOCOL.relative_to(REPO)),
        "protocol_sha256": sha256_path(PROTOCOL),
        "script_path": str(Path(__file__).relative_to(REPO)),
        "script_sha256": sha256_path(Path(__file__)),
        "command": command,
        "run_started_utc": run_start,
        "environment": code_environment(),
    }
    if provenance["git_status_before_run"]:
        raise RuntimeError(
            "Refusing to run with a dirty working tree. Commit protocol and implementation first; generated results must be written after this clean preflight."
        )
    timing = make_timing(case["alpha_over_pi"], case["beta_over_pi"], fixed["J"], fixed["h"])
    system = build_system(
        n_chain=int(fixed["N_chain"]), jcoupling=float(fixed["J"]), hfield=float(fixed["h"]),
        boundary=case["boundary_condition"], contact=contact, gamma1=float(fixed["TLS_amplitude_damping_gamma1"]),
    )
    ratios = np.asarray(measurement["matched_detuning_ratios_omega_d_over_Omega_over_2"], dtype=float)
    values: list[float] = []
    for index, ratio in enumerate(ratios, start=1):
        value = response_at_ratio(
            system, timing, ratio=float(ratio), g=float(fixed["g"]), periods=int(measurement["periods"]),
            samples_per_half=int(measurement["samples_per_half_step"]), discard_periods=int(measurement["discard_periods"]),
        )
        values.append(value)
        print(f"[{case['case_id']}][m={contact}] {index}/{len(ratios)} r={ratio:.3f} A_TLS={value:.10g}", flush=True)
    raw = np.asarray(values, dtype=float)
    result: dict[str, Any] = {
        "schema": "gate_a_v2_full_model_result_v1",
        "case": case,
        "contact_site_m": int(contact),
        "preparation": {
            "chain": protocol["physical_initial_state"]["chain_pure_state"],
            "TLS": protocol["physical_initial_state"]["TLS_state"],
            "independence_declaration": protocol["physical_initial_state"]["independence_declaration"],
            "floquet_pair_selected_for_full_model": False,
            "B0_constructed_for_full_model": False,
        },
        "timing": {"T1": timing.t1, "T2": timing.t2, "T": timing.period, "Omega": timing.omega, "Omega_over_2": timing.omega_over_2},
        "detuning_ratios_omega_d_over_Omega_over_2": ratios.tolist(),
        "raw_A_TLS": raw.tolist(),
        "normalized_shape": (raw / max(float(np.linalg.norm(raw)), 1e-15)).tolist(),
        "spectral_weight_ratio_grid": float(np.trapezoid(raw**2, ratios)),
        "spectral_weight_angular_frequency": float(np.trapezoid(raw**2, ratios * timing.omega_over_2)),
        "provenance": {**provenance, "run_finished_utc": utc_now()},
    }
    result["result_sha256_excluding_self"] = sha256_canonical_without_field(result, "result_sha256_excluding_self")
    filename = f"{case['case_id']}__m{contact}.json"
    destination = output_dir / filename
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL)
    parser.add_argument("--include-heldout", action="store_true", help="Explicitly include heldout_topological_obc_v2; not permitted by default.")
    parser.add_argument("--case", action="append", default=[], help="Run only one named case; repeatable.")
    parser.add_argument("--contact", type=int, action="append", default=[], help="Run only one listed contact; repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="Validate provenance and print the planned cases without propagation.")
    args = parser.parse_args()
    if args.protocol.resolve() != PROTOCOL.resolve():
        raise SystemExit("Gate A v2 is locked to the repository protocol path for provenance integrity.")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if protocol["status"] != "prospectively_frozen_public_commit_required_for_run":
        raise SystemExit(f"Unexpected protocol status: {protocol['status']}")
    all_cases = {case["case_id"]: case for case in protocol["controls"]}
    default_cases = ["topological_obc_production_v2", "topological_pbc_same_drive_v2", "trivial_obc_control_v2"]
    case_ids = args.case if args.case else default_cases
    if args.include_heldout and "heldout_topological_obc_v2" not in case_ids:
        case_ids.append("heldout_topological_obc_v2")
    if not args.include_heldout and "heldout_topological_obc_v2" in case_ids:
        raise SystemExit("The held-out drive requires --include-heldout and a completed primary-control decision audit.")
    unknown_cases = [case_id for case_id in case_ids if case_id not in all_cases]
    if unknown_cases:
        raise SystemExit(f"Unknown case(s): {unknown_cases}")
    contacts = args.contact if args.contact else [
        protocol["full_model_measurement_protocol"]["probe_contacts"]["edge_contact_m"],
        protocol["full_model_measurement_protocol"]["probe_contacts"]["bulk_reference_m"],
    ]
    if sorted(set(contacts)) != sorted(contacts) or any(contact not in range(int(protocol["fixed_chain_TLS_model"]["N_chain"])) for contact in contacts):
        raise SystemExit("Contacts must be distinct valid chain-site integers.")

    run_tag = f"{protocol['protocol_version']}__{sha256_path(PROTOCOL)[:12]}"
    output_dir = RESULTS_ROOT / run_tag / "primary_controls"
    command = [sys.executable, str(Path(__file__).relative_to(REPO)), *sys.argv[1:]]
    print(json.dumps({"planned_cases": case_ids, "contacts": contacts, "output_dir": str(output_dir.relative_to(REPO)), "protocol_sha256": sha256_path(PROTOCOL)}, indent=2))
    if args.dry_run:
        git = git_provenance()
        if git["git_status_before_run"]:
            raise SystemExit("Dry-run preflight failed: working tree is dirty; commit protocol and implementation first.")
        return
    output_dir.mkdir(parents=True, exist_ok=False)
    written: list[str] = []
    for case_id in case_ids:
        for contact in contacts:
            written.append(str(run_one(all_cases[case_id], contact, protocol, output_dir, command).relative_to(REPO)))
    manifest = {
        "schema": "gate_a_v2_full_model_manifest_v1",
        "protocol_sha256": sha256_path(PROTOCOL),
        "git_commit": git_provenance()["git_commit"],
        "run_directory": str(output_dir.relative_to(REPO)),
        "result_files": written,
        "result_file_sha256": {path: sha256_path(REPO / path) for path in written},
        "manifest_created_utc": utc_now(),
    }
    (output_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

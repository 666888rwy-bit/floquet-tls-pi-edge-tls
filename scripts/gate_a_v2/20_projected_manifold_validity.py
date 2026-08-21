#!/usr/bin/env python3
"""Gate B: retained-weight and projected-manifold validity under Gate A v2 preparation.

This script is intentionally separate from the full-model topology control.
It reads one completed Gate A v2 full-model result and then constructs a
Floquet local manifold for the same drive, boundary condition, and contact.
The full initial state is never redefined: its chain factor |up_z>^N is
projected into the selected K=2 and K=4 chain subspaces and the retained
weights p_K are reported before the reduced response is evaluated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm, schur

REPO = Path(__file__).resolve().parents[2]
PROTOCOL = REPO / "protocols/gate_a_v2/gate_a_v2_protocol.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dkron(factors: list[np.ndarray]) -> np.ndarray:
    out = np.array([[1.0 + 0.0j]])
    for factor in factors:
        out = np.kron(out, factor)
    return out


def dop(op: np.ndarray, site: int, n: int, identity: np.ndarray) -> np.ndarray:
    return dkron([op if j == site else identity for j in range(n)])


def propagator(evals: np.ndarray, evecs: np.ndarray, time: float) -> np.ndarray:
    return (evecs * np.exp(-1j * evals * time)) @ evecs.conj().T


def phasor(times: np.ndarray, values: np.ndarray, discard_time: float, omega: float) -> float:
    keep = times >= discard_time
    tt, yy = times[keep], values[keep]
    yy = yy - yy.mean()
    return float(abs(2.0 * np.trapezoid(yy * np.exp(1j * omega * tt / 2.0), tt) / (tt[-1] - tt[0])))


def circle_pi(phi_a: float, phi_b: float) -> float:
    return float(abs(np.angle(np.exp(1j * (phi_b - phi_a - np.pi)))))


def build_channels(case: dict[str, Any], contact: int, protocol: dict[str, Any]) -> dict[str, Any]:
    fixed = protocol["fixed_chain_TLS_model"]
    n, jcoupling, hfield = int(fixed["N_chain"]), float(fixed["J"]), float(fixed["h"])
    alpha, beta = case["alpha_over_pi"] * np.pi, case["beta_over_pi"] * np.pi
    t1, t2 = beta / (2 * jcoupling), alpha / (2 * hfield)
    period, omega = t1 + t2, 2 * np.pi / (t1 + t2)
    i2 = np.eye(2, dtype=complex)
    x2 = np.array([[0., 1.], [1., 0.]], dtype=complex)
    z2 = np.diag([1., -1.]).astype(complex)
    sm2 = np.array([[0., 1.], [0., 0.]], dtype=complex)
    xs = [dop(x2, m, n, i2) for m in range(n)]
    zs = [dop(z2, m, n, i2) for m in range(n)]
    sm = dop(sm2, contact, n, i2)
    links = [(m, m + 1) for m in range(n - 1)] + ([(n - 1, 0)] if case["boundary_condition"] == "PBC" else [])
    h1 = sum((-jcoupling * zs[a] @ zs[b] for a, b in links), start=np.zeros((2**n, 2**n), dtype=complex))
    h2 = sum((-hfield * xx for xx in xs), start=np.zeros((2**n, 2**n), dtype=complex))
    e1, v1 = np.linalg.eigh(h1); e2, v2 = np.linalg.eigh(h2)
    u1, u2 = propagator(e1, v1, t1), propagator(e2, v2, t2)
    triangular, vectors = schur(u2 @ u1, output="complex")
    phases = np.angle(np.diag(triangular)); eps = -phases / period
    b0 = np.zeros((2**n, 2**n), dtype=complex)
    times = np.linspace(0, period, 241)
    for index, time in enumerate(times):
        evolution = propagator(e1, v1, time) if time <= t1 + 1e-14 else propagator(e2, v2, time - t1) @ u1
        modes = evolution @ vectors * np.exp(1j * eps * time)[None, :]
        b0 += (0.5 if index in (0, len(times) - 1) else 1.0) * (modes.conj().T @ sm @ modes)
    b0 *= (times[1] - times[0]) / period
    candidates = []
    for a in range(2**n):
        for b in range(a + 1, 2**n):
            mismatch = circle_pi(phases[a], phases[b])
            if mismatch <= .02:
                candidates.append((float(max(abs(b0[a,b]), abs(b0[b,a]))), mismatch, a, b))
    if not candidates:
        raise RuntimeError("No near-pi pair eligible for Gate B manifold construction.")
    candidates.sort(key=lambda row: (row[0], -row[1]), reverse=True)
    score, mismatch, a, b = candidates[0]
    target = [int(a), int(b)]
    ranking=[]
    for q in range(2**n):
        if q in target: continue
        weight=float(sum(abs(b0[q,p])**2+abs(b0[p,q])**2 for p in target))
        detuning=min(abs(np.angle(np.exp(1j*(phases[q]-phases[p]))))/period for p in target)
        ranking.append((weight/(detuning**2+(0.05*omega)**2),q,weight,detuning))
    ranking.sort(reverse=True)
    return {"vectors":vectors,"eps":eps,"b0":b0,"target":target,"indices":{2:target,4:target+[int(q) for _,q,_,_ in ranking[:2]]},"timing":{"T1":t1,"T2":t2,"T":period,"Omega":omega,"Omega_over_2":omega/2},"selection":{"indices":target,"local_B0_score":score,"pi_mismatch_rad":mismatch,"eligible_pair_count":len(candidates),"floquet_index_disclaimer":"Schur numerical ordering metadata, not cross-platform physical labels."}}


def effective_response(indices: list[int], channel: dict[str,Any], initial_coeff: np.ndarray, ratios: np.ndarray, protocol: dict[str,Any]) -> np.ndarray:
    fixed, measurement = protocol["fixed_chain_TLS_model"], protocol["full_model_measurement_protocol"]
    kdim=len(indices); i2=np.eye(2,dtype=complex); z2=np.diag([1.,-1.]).astype(complex); sm2=np.array([[0.,1.],[0.,0.]],complex)
    eps=channel["eps"][indices]; eps=eps-np.mean(eps); bb=channel["b0"][np.ix_(indices,indices)]
    timing=channel["timing"]; dim=2*kdim; observable=np.kron(np.eye(kdim),sm2); collapse=np.sqrt(float(fixed["TLS_amplitude_damping_gamma1"]))*observable; cdc=collapse.conj().T@collapse; identity=np.eye(dim,dtype=complex)
    # Projected chain pure state is already normalized by sqrt(p_K).
    statevec=np.zeros(dim,dtype=complex); statevec[0::2]=initial_coeff
    rho0=np.outer(statevec,statevec.conj()).reshape(-1,order="F")
    out=[]
    for ratio in ratios:
        hamiltonian=np.kron(np.diag(eps),i2)+np.kron(np.eye(kdim),-.5*ratio*timing["Omega_over_2"]*z2)+float(fixed["g"])*(np.kron(bb.conj().T,sm2)+np.kron(bb,sm2.conj().T))
        generator=-1j*(np.kron(identity,hamiltonian)-np.kron(hamiltonian.T,identity))+np.kron(collapse.conj(),collapse)-.5*np.kron(identity,cdc)-.5*np.kron(cdc.T,identity)
        u1=expm(generator*(timing["T1"]/int(measurement["samples_per_half_step"]))); u2=expm(generator*(timing["T2"]/int(measurement["samples_per_half_step"])))
        rho=rho0.copy(); tt=[]; yy=[]; t=0.
        for _ in range(int(measurement["periods"])):
            for __ in range(int(measurement["samples_per_half_step"])):
                tt.append(t); yy.append(np.trace(observable@rho.reshape((dim,dim),order="F"))); rho=u1@rho; t+=timing["T1"]/int(measurement["samples_per_half_step"])
            for __ in range(int(measurement["samples_per_half_step"])):
                tt.append(t); yy.append(np.trace(observable@rho.reshape((dim,dim),order="F"))); rho=u2@rho; t+=timing["T2"]/int(measurement["samples_per_half_step"])
        out.append(phasor(np.asarray(tt),np.asarray(yy),int(measurement["discard_periods"])*timing["T"],timing["Omega"]))
    return np.asarray(out)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-result",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    protocol=json.loads(PROTOCOL.read_text(encoding="utf-8")); full=json.loads(args.full_result.read_text(encoding="utf-8"))
    if full["preparation"]["floquet_pair_selected_for_full_model"] or full["preparation"]["B0_constructed_for_full_model"]: raise SystemExit("Input is not a Gate A v2 pair-independent full-model result.")
    channel=build_channels(full["case"],int(full["contact_site_m"]),protocol)
    psi0=np.zeros(2**int(protocol["fixed_chain_TLS_model"]["N_chain"]),complex); psi0[0]=1.
    ratios=np.asarray(full["detuning_ratios_omega_d_over_Omega_over_2"],float); full_a=np.asarray(full["raw_A_TLS"],float); results=[]
    for kdim,inds in channel["indices"].items():
        coeff=channel["vectors"][:,inds].conj().T@psi0; pk=float(np.vdot(coeff,coeff).real)
        row={"K":kdim,"indices":[int(q) for q in inds],"p_K":pk}
        if pk<=1e-12: row["status"]="undefined_retained_weight_at_or_below_1e-12"
        else:
            a = effective_response(inds, channel, coeff / np.sqrt(pk), ratios, protocol)
            a_normalized = a / max(float(np.linalg.norm(a)), 1e-15)
            full_normalized = full_a / max(float(np.linalg.norm(full_a)), 1e-15)
            row.update({
                "status": "completed",
                "raw_A_TLS": a.tolist(),
                "normalized_shape": a_normalized.tolist(),
                "epsilon_spec_normalized_shape": float(np.linalg.norm(a_normalized - full_normalized)),
                "raw_peak_ratio_reduced_over_full": float(np.max(a) / max(float(np.max(full_a)), 1e-15)),
            })
        results.append(row)
    provenance={"protocol_sha256":sha256(PROTOCOL),"script_sha256":sha256(Path(__file__)),"source_full_result":str(args.full_result),"source_full_result_sha256":sha256(args.full_result),"git_commit":subprocess.check_output(["git","-C",str(REPO),"rev-parse","HEAD"],text=True).strip(),"run_started_utc":utc_now(),"command":[sys.executable,str(Path(__file__).relative_to(REPO)),*sys.argv[1:]]}
    payload={"schema":"gate_a_v2_projected_manifold_result_v1","source_case":full["case"],"contact_site_m":full["contact_site_m"],"selection_for_manifold_only":channel["selection"],"timing":channel["timing"],"results":results,"provenance":{**provenance,"run_finished_utc":utc_now()}}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(args.output)

if __name__=="__main__": main()

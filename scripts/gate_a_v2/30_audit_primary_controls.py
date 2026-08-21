#!/usr/bin/env python3
"""Read-only Gate A v2 primary-control audit.

Inputs are the six exact full-model JSON files plus MANIFEST.json.  The script
never modifies a spectrum and never selects a Floquet pair.  It verifies file
hashes, evaluates the frozen finite-system metrics, reports directional ratios
requested for interpretation, and writes JSON/Markdown/PNG/PDF artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
PROTOCOL = REPO / "protocols/gate_a_v2/gate_a_v2_protocol.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized(a: np.ndarray) -> np.ndarray:
    return a / max(float(np.linalg.norm(a)), 1e-15)


def local_maxima(a: np.ndarray) -> list[int]:
    return [i for i in range(1, len(a)-1) if a[i] > a[i-1] and a[i] > a[i+1]]


def feature_summary(r: np.ndarray, a: np.ndarray) -> dict[str, Any]:
    peak = float(np.max(a)); maxima = local_maxima(a)
    tied = [float(r[i]) for i, value in enumerate(a) if np.isclose(value, peak, rtol=1e-12, atol=1e-15)]
    selected = [i for i in maxima if a[i] >= .70 * peak]
    splitting: dict[str, Any] = {"status": "not_resolved_on_frozen_grid"}
    if len(selected) >= 2:
        pairs = [(i, j) for i in selected for j in selected if j > i and j-i >= 2]
        if pairs:
            i, j = max(pairs, key=lambda pair: min(a[pair[0]], a[pair[1]]))
            splitting = {"status": "resolved_by_protocol_rule", "peak_ratios": [float(r[i]), float(r[j])], "separation_in_ratio": float(r[j]-r[i])}
    imax = int(np.argmax(a)); half = peak/2
    left = next((i for i in range(imax-1, -1, -1) if a[i] <= half), None)
    right = next((i for i in range(imax+1, len(a)) if a[i] <= half), None)
    linewidth: dict[str, Any] = {"status": "censored_by_grid"}
    if left is not None and right is not None:
        def cross(i0: int, i1: int) -> float:
            return float(r[i0] + (half-a[i0])*(r[i1]-r[i0])/(a[i1]-a[i0]))
        xleft = cross(left, left+1); xright = cross(right-1, right)
        linewidth = {"status": "reported_FWHM_linear_interpolation", "FWHM_in_ratio": float(xright-xleft), "crossings": [xleft,xright]}
    return {"raw_peak": peak, "peak_ratio_grid_locations": tied, "splitting": splitting, "linewidth": linewidth}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(); run_dir = args.run_dir
    protocol = load(PROTOCOL); manifest = load(run_dir / "MANIFEST.json")
    if manifest["protocol_sha256"] != sha256(PROTOCOL):
        raise SystemExit("Protocol hash mismatch; refusing audit.")
    records: dict[tuple[str,int],dict[str,Any]] = {}
    integrity = {}
    for relative, expected in manifest["result_file_sha256"].items():
        path = REPO / relative; actual = sha256(path); integrity[relative] = {"expected": expected, "actual": actual, "matches": actual == expected}
        if actual != expected: raise SystemExit(f"Result hash mismatch: {relative}")
        record=load(path); records[(record["case"]["case_id"],record["contact_site_m"])]=record
    top="topological_obc_production_v2"; controls=["topological_pbc_same_drive_v2","trivial_obc_control_v2"]
    all_ids=[top,*controls]; ratios=np.asarray(records[(top,0)]["detuning_ratios_omega_d_over_Omega_over_2"],float)
    table={}
    for case_id in all_ids:
        table[case_id]={}
        for contact in [0,3]:
            rec=records[(case_id,contact)]; a=np.asarray(rec["raw_A_TLS"],float)
            if rec["preparation"]["floquet_pair_selected_for_full_model"] or rec["preparation"]["B0_constructed_for_full_model"]: raise SystemExit("Pair-dependent full result found.")
            table[case_id][f"m{contact}"]={"spectral_weight_ratio_grid":float(np.trapezoid(a*a,ratios)),"spectral_weight_angular_frequency":float(np.trapezoid(a*a,ratios*rec["timing"]["Omega_over_2"])),"features":feature_summary(ratios,a),"raw_A_TLS":a.tolist(),"normalized_shape":normalized(a).tolist()}
        table[case_id]["R_EB_m0_over_m3"]=float(table[case_id]["m0"]["spectral_weight_ratio_grid"]/max(table[case_id]["m3"]["spectral_weight_ratio_grid"],1e-15))
    decisions={}
    for cid in controls:
        wtop=table[top]["m0"]["spectral_weight_ratio_grid"]; wctrl=table[cid]["m0"]["spectral_weight_ratio_grid"]
        d=float(np.linalg.norm(np.asarray(table[top]["m0"]["normalized_shape"])-np.asarray(table[cid]["m0"]["normalized_shape"])))
        reb_dir=float(table[top]["R_EB_m0_over_m3"]/max(table[cid]["R_EB_m0_over_m3"],1e-15))
        directional=wtop/max(wctrl,1e-15); symmetric=max(directional,1/directional)
        decisions[cid]={"directional_W_topological_OBC_over_control":directional,"frozen_symmetric_C_W":symmetric,"shape_distance_D":d,"directional_C_EB":reb_dir,"passes_frozen_symmetric_weight_threshold":symmetric>=1.50,"passes_shape_threshold":d>=.30,"passes_edge_reference_threshold":reb_dir>=1.50,"passes_directional_weight_threshold_requested_for_interpretation":directional>=1.50}
    frozen_pass=all(v["passes_frozen_symmetric_weight_threshold"] and v["passes_shape_threshold"] and v["passes_edge_reference_threshold"] for v in decisions.values())
    directional_pass=all(v["passes_directional_weight_threshold_requested_for_interpretation"] and v["passes_shape_threshold"] and v["passes_edge_reference_threshold"] for v in decisions.values())
    audit={"schema":"gate_a_v2_primary_audit_v1","manifest_sha256":sha256(run_dir/"MANIFEST.json"),"protocol_sha256":sha256(PROTOCOL),"integrity":integrity,"metric_table":table,"control_comparisons":decisions,"frozen_protocol_decision":"pass_to_heldout" if frozen_pass else "do_not_run_heldout","directional_interpretation_decision":"pass_to_heldout" if directional_pass else "do_not_run_heldout","critical_protocol_note":"The committed v2 protocol defined C_W symmetrically as max(W_top/W_control,W_control/W_top), whereas the owner requested directional W_top/W_control ratios. Both are reported without retroactive protocol modification; the directional decision is the conservative manuscript-relevant interpretation."}
    (run_dir/"PRIMARY_AUDIT.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
    md=["# Gate A v2 primary-control audit","",f"**Frozen protocol SHA-256:** `{audit['protocol_sha256']}`  ",f"**Manifest SHA-256:** `{audit['manifest_sha256']}`","","> This is a finite N=6 audit under a common product-state preparation. It is not a thermodynamic-limit or phase-boundary claim.","", "| Control | W_top/W_control at m=0 | D(shape) | R_EB(top)/R_EB(control) | Directional decision |", "|---|---:|---:|---:|---|"]
    for cid,v in decisions.items(): md.append(f"| {cid} | {v['directional_W_topological_OBC_over_control']:.4g} | {v['shape_distance_D']:.4g} | {v['directional_C_EB']:.4g} | {'pass' if (v['passes_directional_weight_threshold_requested_for_interpretation'] and v['passes_shape_threshold'] and v['passes_edge_reference_threshold']) else 'do not run held-out'} |")
    md += ["",f"**Frozen symmetric-rule decision:** `{audit['frozen_protocol_decision']}`.",f"**Conservative directional interpretation:** `{audit['directional_interpretation_decision']}`.","", "The protocol's symmetric C_W definition and the requested directional W ratio are both retained; the latter is not inserted retroactively into the frozen decision rule. No held-out run is authorized unless the conservative directional interpretation is `pass_to_heldout`.","", "## Integrity", "", "All six source files match the SHA-256 values in `MANIFEST.json`. Every source record declares `floquet_pair_selected_for_full_model=false` and `B0_constructed_for_full_model=false`."]
    (run_dir/"PRIMARY_AUDIT.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    fig,axes=plt.subplots(1,2,figsize=(11,4.2),constrained_layout=True); colors={top:"black",controls[0]:"#0072b2",controls[1]:"#d55e00"}
    for cid in all_ids:
        for contact,ax in zip([0,3],axes):
            a=np.asarray(table[cid][f"m{contact}"]["raw_A_TLS"]); ax.plot(ratios,a,marker="o",ms=3.5,lw=1.8,color=colors[cid],label=cid.replace("_v2",""))
            ax.set(title=f"common preparation, TLS contact m={contact}",xlabel=r"$\omega_d/(\Omega/2)$",ylabel=r"raw $A_{\rm TLS}$"); ax.grid(alpha=.25); ax.axvline(1.,color=".5",ls=":",lw=.9)
    axes[0].legend(fontsize=7); fig.savefig(run_dir/"PRIMARY_CONTROLS_RAW_SPECTRA.png",dpi=260); fig.savefig(run_dir/"PRIMARY_CONTROLS_RAW_SPECTRA.pdf"); plt.close(fig)
    print(json.dumps({"frozen_protocol_decision":audit["frozen_protocol_decision"],"directional_interpretation_decision":audit["directional_interpretation_decision"],"control_comparisons":decisions},indent=2))

if __name__=="__main__": main()

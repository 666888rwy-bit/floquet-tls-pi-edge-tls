#!/usr/bin/env python3
"""Exact N=4 Gate D1 raw-weight screen; no Floquet-pair preparation or reduction."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[2]
PROTOCOL=REPO/'protocols/gate_d1/gate_d1_n4_nupi_weight_protocol.json'
HELPER=REPO/'scripts/gate_a_v2/10_full_model_common_preparation.py'
OUTROOT=REPO/'results/gate_d1'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def canonical(payload): return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load_helper():
    spec=importlib.util.spec_from_file_location('gate_d_fullv2',HELPER); module=importlib.util.module_from_spec(spec); sys.modules['gate_d_fullv2']=module; spec.loader.exec_module(module); return module
def valid(path,task,protocol_sha):
    try:
        payload=json.loads(Path(path).read_text()); observed=payload.pop('result_sha256_excluding_self')
        return canonical(payload)==observed and payload.get('task')==task and payload.get('provenance',{}).get('protocol_sha256')==protocol_sha
    except Exception: return False
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--drive',action='append',default=[]); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--resume',action='store_true'); args=ap.parse_args()
    p=json.loads(PROTOCOL.read_text()); common=p['common_physical_protocol']; psha=sha(PROTOCOL); out=OUTROOT/f"{p['protocol_version']}__{psha[:12]}"
    drives=[d for d in p['selected_drives'] if not args.drive or d['id'] in args.drive]
    if not drives: raise SystemExit('No selected drives')
    dirty=subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True).strip()
    if dirty: raise SystemExit('Refusing dirty worktree before Gate D1 run.')
    completed=[]; pending=[]
    for d in drives:
        dest=out/f"{d['id']}.json"
        if dest.exists() and valid(dest,d,psha): completed.append(d['id'])
        elif dest.exists(): raise SystemExit(f'Invalid existing result: {dest}')
        else: pending.append(d)
    if out.exists() and pending and not args.resume: raise SystemExit('Output directory exists. Use --resume after validation.')
    print(json.dumps({'requested':[d['id'] for d in drives],'skipped_valid':completed,'pending':[d['id'] for d in pending],'output_dir':str(out.relative_to(REPO)),'resume':args.resume},indent=2))
    if args.dry_run:return
    out.mkdir(parents=True,exist_ok=True); full=load_helper(); ratios=np.asarray(common['detuning_ratios_omega_d_over_Omega_over_2'],float); commit=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(); written=[]
    for d in pending:
        start=utc(); T=d['T']; g=common['gT_target']/T; gamma=common['gamma1T_target']/T
        timing=full.make_timing(d['alpha_over_pi'],d['beta_over_pi'],common['J'],common['h'])
        if not np.isclose(T,timing.period,rtol=0,atol=1e-12): raise SystemExit(f"Timing mismatch at {d['id']}")
        system=full.build_system(n_chain=common['N_chain'],jcoupling=common['J'],hfield=common['h'],boundary=common['boundary'],contact=common['TLS_contact_site'],gamma1=gamma)
        values=[]
        for n,ratio in enumerate(ratios,1):
            value=full.response_at_ratio(system,timing,ratio=float(ratio),g=g,periods=common['periods'],samples_per_half=common['samples_per_half_step'],discard_periods=common['discard_periods']); values.append(value); print(f"[{d['id']}] {n}/{len(ratios)} r={ratio:.3f} A={value:.9g}",flush=True)
        raw=np.asarray(values,float); payload={'schema':'gate_d1_n4_full_model_result_v1','task':d,'common_protocol':{'N_chain':common['N_chain'],'boundary':common['boundary'],'TLS_contact_site':common['TLS_contact_site'],'initial_chain_state':common['initial_chain_state'],'initial_TLS_state':common['initial_TLS_state'],'floquet_pair_selected':False,'B0_constructed':False,'gT_target':common['gT_target'],'gamma1T_target':common['gamma1T_target'],'periods':common['periods'],'discard_periods':common['discard_periods'],'samples_per_half_step':common['samples_per_half_step']},'timing':{'T':timing.period,'Omega':timing.omega,'g':g,'gamma1':gamma,'gT':g*timing.period,'gamma1T':gamma*timing.period,'total_time':common['periods']*timing.period},'ratios':ratios.tolist(),'raw_A_TLS':raw.tolist(),'normalized_shape':(raw/max(float(np.linalg.norm(raw)),1e-15)).tolist(),'W_r':float(np.trapezoid(raw**2,ratios)),'provenance':{'protocol_sha256':psha,'script_sha256':sha(Path(__file__)),'git_commit':commit,'run_started_utc':start,'run_finished_utc':utc(),'command':[sys.executable,str(Path(__file__).relative_to(REPO)),*sys.argv[1:]]}}
        payload['result_sha256_excluding_self']=canonical(payload); dest=out/f"{d['id']}.json"; dest.write_text(json.dumps(payload,indent=2)); written.append(str(dest.relative_to(REPO)))
    paths=[]
    for d in drives:
        dest=out/f"{d['id']}.json"
        if not valid(dest,d,psha): raise SystemExit(f'Post-run validation failed: {dest.name}')
        paths.append(str(dest.relative_to(REPO)))
    manifest={'schema':'gate_d1_manifest_v1','protocol_sha256':psha,'git_commit':commit,'results':paths,'sha256':{x:sha(REPO/x) for x in paths},'created_utc':utc(),'resume_metadata':{'resumed':args.resume,'skipped_valid':completed,'newly_written':[Path(x).stem for x in written]}}
    (out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)); print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()

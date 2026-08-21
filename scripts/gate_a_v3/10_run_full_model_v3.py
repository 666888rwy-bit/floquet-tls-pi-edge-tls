#!/usr/bin/env python3
"""Exact Gate A v3 common-preparation full-model production runner."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
PROTOCOL = REPO / 'protocols/gate_a_v3/gate_a_v3_protocol.json'
HELPER = REPO / 'scripts/gate_a_v2/10_full_model_common_preparation.py'
OUTROOT = REPO / 'results/gate_a_v3'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def canonical_sha(payload): return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def load_helper():
    spec = importlib.util.spec_from_file_location('fullv2', HELPER)
    module = importlib.util.module_from_spec(spec)
    sys.modules['fullv2'] = module
    spec.loader.exec_module(module)
    return module

def resolve(protocol, section):
    group = protocol['matched_groups'][section['group']]
    drive = group['drives'][section['drive']]
    return {
        'alpha_over_pi': drive['alpha_over_pi'], 'beta_over_pi': drive['beta_over_pi'],
        'nu0': drive.get('nu0'), 'nupi': drive.get('nupi'), 'margin_rad': drive.get('margin_rad'),
        'g': group['g'], 'gamma1': group['gamma1'],
        'periods': section.get('periods', group['periods']),
        'discard_periods': section.get('discard_periods', group['discard_periods']),
    }

def build_tasks(protocol):
    tasks=[]
    for item in protocol['primary_full_model_runs']:
        base=resolve(protocol,item)
        for contact in item['contacts']:
            tasks.append({'task_id':item['run_id'],'boundary':item['boundary'],'contact':contact,'samples_per_half_step':4,**base})
    spatial=protocol['spatial_profile']; base=resolve(protocol,spatial)
    for contact in spatial['new_contacts_to_run']:
        tasks.append({'task_id':f'production_spatial_m{contact}','boundary':spatial['boundary'],'contact':contact,'samples_per_half_step':4,**base})
    convergence=protocol['numerical_convergence']; base=resolve(protocol,convergence)
    for variant in convergence['new_variants']:
        task={'task_id':f"convergence_s{variant['samples_per_half_step']}_d{variant['discard_periods']}", 'boundary':convergence['boundary'], 'contact':convergence['contact'], **base}
        task.update(variant); tasks.append(task)
    held=protocol['heldout_same_drive_PBC']
    for contact in held['contacts']:
        tasks.append({'task_id':f'heldout_PBC_m{contact}','boundary':held['boundary'],'contact':contact,'samples_per_half_step':4,'alpha_over_pi':held['alpha_over_pi'],'beta_over_pi':held['beta_over_pi'],'nu0':held['nu0'],'nupi':held['nupi'],'margin_rad':held['margin_rad'],'g':held['g'],'gamma1':held['gamma1'],'periods':held['periods'],'discard_periods':held['discard_periods']})
    return tasks

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--task',action='append',default=[])
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    protocol=json.loads(PROTOCOL.read_text())
    if protocol['status']!='prospectively_frozen_public_commit_required_for_run': raise SystemExit('Unexpected protocol status')
    if subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True).strip(): raise SystemExit('Refusing dirty worktree before v3 run.')
    tasks=[task for task in build_tasks(protocol) if not args.task or task['task_id'] in args.task]
    if not tasks: raise SystemExit('No tasks selected')
    out=OUTROOT/f"{protocol['protocol_version']}__{sha(PROTOCOL)[:12]}"
    print(json.dumps({'tasks':[task['task_id'] for task in tasks],'output_dir':str(out.relative_to(REPO))},indent=2))
    if args.dry_run: return
    out.mkdir(parents=True,exist_ok=False)
    full=load_helper(); ratios=np.asarray(protocol['readout']['detuning_ratios_omega_d_over_Omega_over_2'],float)
    commit=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(); written=[]
    for task in tasks:
        start=utc()
        timing=full.make_timing(task['alpha_over_pi'],task['beta_over_pi'],1.0,1.0)
        system=full.build_system(n_chain=6,jcoupling=1.0,hfield=1.0,boundary=task['boundary'],contact=task['contact'],gamma1=task['gamma1'])
        values=[]
        for number,ratio in enumerate(ratios,1):
            value=full.response_at_ratio(system,timing,ratio=float(ratio),g=task['g'],periods=task['periods'],samples_per_half=task['samples_per_half_step'],discard_periods=task['discard_periods'])
            values.append(value); print(f"[{task['task_id']}] {number}/{len(ratios)} r={ratio:.3f} A={value:.9g}",flush=True)
        raw=np.asarray(values,float)
        payload={
            'schema':'gate_a_v3_full_model_result_v1', 'task':task,
            'preparation':{'chain':protocol['common_model']['initial_chain_state'],'TLS':protocol['common_model']['initial_TLS_state'],'floquet_pair_selected_for_full_model':False,'B0_constructed_for_full_model':False,'independence_declaration':protocol['common_model']['full_model_declaration']},
            'timing':{'T1':timing.t1,'T2':timing.t2,'T':timing.period,'Omega':timing.omega,'Omega_over_2':timing.omega_over_2,'gT':task['g']*timing.period,'gamma1T':task['gamma1']*timing.period,'total_time':task['periods']*timing.period},
            'ratios':ratios.tolist(),'raw_A_TLS':raw.tolist(),'normalized_shape':(raw/max(float(np.linalg.norm(raw)),1e-15)).tolist(),'W_r':float(np.trapezoid(raw**2,ratios)),
            'provenance':{'protocol_sha256':sha(PROTOCOL),'script_sha256':sha(Path(__file__)),'git_commit':commit,'run_started_utc':start,'run_finished_utc':utc(),'command':[sys.executable,str(Path(__file__).relative_to(REPO)),*sys.argv[1:]]}
        }
        payload['result_sha256_excluding_self']=canonical_sha(payload)
        destination=out/f"{task['task_id']}.json"; destination.write_text(json.dumps(payload,indent=2)); written.append(str(destination.relative_to(REPO)))
    manifest={'schema':'gate_a_v3_manifest_v1','protocol_sha256':sha(PROTOCOL),'git_commit':commit,'results':written,'sha256':{item:sha(REPO/item) for item in written},'created_utc':utc()}
    (out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)); print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()

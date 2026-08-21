#!/usr/bin/env python3
"""Gate B2: prospectively frozen preparation-compatible manifold benchmark."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO=Path(__file__).resolve().parents[2]
PROTOCOL=REPO/'protocols/gate_a_v2/gate_b2_initial_support_manifold_protocol.json'
HELPER=REPO/'scripts/gate_a_v2/20_projected_manifold_validity.py'

def utc():return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(a):return a/max(float(np.linalg.norm(a)),1e-15)
def load_helper():
    spec=importlib.util.spec_from_file_location('gate_b_helpers',HELPER);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def uniq(seq):
    out=[]
    for q in seq:
        if int(q) not in out:out.append(int(q))
    return out

def evaluate_selection(name,indices,channel,psi,ratios,full_a,protocol,helper):
    coeff=channel['vectors'][:,indices].conj().T@psi;p=float(np.vdot(coeff,coeff).real)
    row={'selection_family':name,'K':len(indices),'indices':[int(q) for q in indices],'p_K':p}
    if p<=1e-12:
        row['status']='undefined_retained_weight_at_or_below_1e-12';return row
    a=helper.effective_response(indices,channel,coeff/np.sqrt(p),ratios,protocol);an=norm(a)
    row.update({'status':'completed','raw_A_TLS':a.tolist(),'normalized_shape':an.tolist(),'epsilon_spec_normalized_shape':float(np.linalg.norm(an-norm(full_a))),'raw_peak_ratio_reduced_over_full':float(np.max(a)/max(float(np.max(full_a)),1e-15)),'spectral_weight_ratio_reduced_over_full':float(np.trapezoid(a*a,ratios)/max(float(np.trapezoid(full_a*full_a,ratios)),1e-15))})
    return row

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=None);args=parser.parse_args()
    protocol=json.loads(PROTOCOL.read_text());
    if protocol['status']!='prospectively_frozen_public_commit_required_for_run':raise SystemExit('Unexpected protocol status')
    if subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True).strip():raise SystemExit('Refusing dirty tree: publicly commit protocol and script before run.')
    helper=load_helper();started=utc();all_rows=[]
    for label,source in protocol['source_full_results'].items():
        source_path=REPO/source;full=json.loads(source_path.read_text());channel=helper.build_channels(full['case'],0,json.loads((REPO/'protocols/gate_a_v2/gate_a_v2_protocol.json').read_text()))
        psi=np.zeros(channel['vectors'].shape[0],complex);psi[0]=1.;overlap=np.abs(channel['vectors'].conj().T@psi)**2;support=[int(q) for q in np.argsort(-overlap)]
        pair=channel['indices'][2];families={}
        families['legacy_resonance_ranked']={4:channel['indices'][4]}
        families['initial_support_ranked']={K:support[:K] for K in [8,16]}
        families['hybrid_pair_plus_initial_support']={K:uniq(pair+support[:max(0,K-2)])[:K] for K in [4,8,16,32]}
        ratios=np.asarray(full['detuning_ratios_omega_d_over_Omega_over_2'],float);full_a=np.asarray(full['raw_A_TLS'],float);rows=[]
        for family,ks in families.items():
            for _,indices in ks.items():rows.append(evaluate_selection(family,indices,channel,psi,ratios,full_a,json.loads((REPO/'protocols/gate_a_v2/gate_a_v2_protocol.json').read_text()),helper))
        by={(r['selection_family'],r['K']):r for r in rows};hy16=by[('hybrid_pair_plus_initial_support',16)];hy32=by[('hybrid_pair_plus_initial_support',32)];legacy=by[('legacy_resonance_ranked',4)]
        decision={'source_label':label,'hybrid_p16_pass':hy16['p_K']>=.90,'legacy_defined':legacy['status']=='completed'}
        if hy16['status']=='completed' and hy32['status']=='completed':
            decision.update({'hybrid_epsilon16_pass':hy16['epsilon_spec_normalized_shape']<=.35,'hybrid_peak16_pass':.50<=hy16['raw_peak_ratio_reduced_over_full']<=2.0,'hybrid_K16_K32_shape_change':float(np.linalg.norm(np.asarray(hy16['normalized_shape'])-np.asarray(hy32['normalized_shape']))),'hybrid_K16_K32_pass':float(np.linalg.norm(np.asarray(hy16['normalized_shape'])-np.asarray(hy32['normalized_shape'])))<=.05})
            if legacy['status']=='completed':decision['hybrid_improvement_pass']=hy16['epsilon_spec_normalized_shape']<=.60*legacy['epsilon_spec_normalized_shape']
        all_rows.append({'source_label':label,'source_full_result':source,'source_full_result_sha256':sha(source_path),'case':full['case'],'local_pair_for_mechanism_only':channel['selection'],'initial_support_coverage_K':{str(target):int(np.searchsorted(np.cumsum(overlap[support]),target)+1) for target in [.5,.8,.9,.95,.99]},'rows':rows,'decision':decision})
    payload={'schema':'gate_b2_initial_support_benchmark_v1','protocol_sha256':sha(PROTOCOL),'script_sha256':sha(Path(__file__)),'git_commit':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),'run_started_utc':started,'run_finished_utc':utc(),'results':all_rows};payload['result_sha256_excluding_self']=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    out=args.output or REPO/'results/gate_a_v2/gate_a_v2.0__00d3477cc81e/gate_b2/GATE_B2_INITIAL_SUPPORT_BENCHMARK.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2));print(out)
if __name__=='__main__':main()

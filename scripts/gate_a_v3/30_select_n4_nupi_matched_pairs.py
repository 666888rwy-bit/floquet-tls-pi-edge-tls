#!/usr/bin/env python3
"""Response-blind N=4 stratified BDI candidate selection for an exploratory nu_pi weight screen."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[2]
ISO=REPO/'scripts/gate_a_v3/01_iso_period_bdi_control_search.py'
OUT=REPO/'results/gate_a_v3/gate_d_n4_weight_screen'
def load_iso():
    spec=importlib.util.spec_from_file_location('gate_a_iso',ISO); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.KS=np.linspace(-np.pi,np.pi,1001,endpoint=False); return m
def choose_diverse(items,n=3,min_distance=0.18):
    out=[]
    for item in sorted(items,key=lambda x:-x['margin_rad']):
        if all(np.hypot(item['alpha_over_pi']-old['alpha_over_pi'],item['beta_over_pi']-old['beta_over_pi'])>=min_distance for old in out): out.append(item)
        if len(out)==n: return out
    return out
def main():
    OUT.mkdir(parents=True,exist_ok=True); m=load_iso(); classes={(0,0):[],(1,0):[],(0,1):[],(1,1):[]}
    # Response-blind grid. T is restricted to keep g=gT/T and gamma=gammaT/T in a moderate interval.
    for alpha in np.linspace(.10,.98,61):
        for beta in np.linspace(.10,.98,61):
            T=float((alpha+beta)*np.pi/2)
            if not (1.20<=T<=2.85): continue
            result=m.inv(alpha*np.pi,beta*np.pi)
            key=(result['nu0'],result['nupi'])
            if result['classified'] and key in classes and result['margin_rad']>=.30:
                result.update({'alpha_over_pi':float(alpha),'beta_over_pi':float(beta),'T':T,'Omega':float(2*np.pi/T),'selection_score':float(result['margin_rad'])})
                classes[key].append(result)
    selected={f'nu{a}{b}':choose_diverse(classes[(a,b)],n=2) for a,b in classes}
    candidate_complete=all(len(points)==2 for points in selected.values())
    payload={'schema':'gate_d_n4_stratified_bdi_selection_v1','candidate_complete':candidate_complete,'selection_stop_note':'If candidate_complete is false, do not run TLS screening; revise the pre-response geometric selection constraints transparently.','closed_chain_convention_source':str(ISO.relative_to(REPO)),'selection_is_response_blind':True,'grid':'alpha/pi,beta/pi in [0.10,0.98], 61x61; retain 1.20<=T<=2.85 and margin>=0.30 rad','selection_rule':'Within each BDI class, rank safe points by the smaller zero/pi bulk gap margin and greedily retain two points separated by Euclidean distance >=0.18 in (alpha/pi,beta/pi). No TLS response, Floquet-pair selection, or local matrix element enters selection.','classes_with_safe_candidate_counts':{f'nu{a}{b}':len(classes[(a,b)]) for a,b in classes},'selected_points_by_class':selected}
    (OUT/'N4_BDI_STRATIFIED_CANDIDATES.json').write_text(json.dumps(payload,indent=2)); print(json.dumps(payload,indent=2))
if __name__=='__main__': main()

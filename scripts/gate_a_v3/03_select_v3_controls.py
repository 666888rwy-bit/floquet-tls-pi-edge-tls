#!/usr/bin/env python3
"""Select deterministic Gate A v3 BDI control points on two matched-period lines."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[2];BASE=REPO/'scripts/gate_a_v3/01_iso_period_bdi_control_search.py';OUT=REPO/'results/gate_a_v3/control_search'
def mod():
 s=importlib.util.spec_from_file_location('bdi',BASE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.KS=np.linspace(-np.pi,np.pi,4001,endpoint=False);return m
def line(m,S,n=2001):
 rec=[]
 for a in np.linspace(max(.04,S-.96),min(.96,S-.04),n):
  b=S-a;r=m.inv(a*np.pi,b*np.pi)
  if r['classified']:r.update({'alpha_over_pi':float(a),'beta_over_pi':float(b),'S_over_pi':float(S),'T':float(S*np.pi/2),'Omega':float(4/S)});rec.append(r)
 return rec
def choose(records,cl,reference=None):
 pool=[r for r in records if (r['nu0'],r['nupi'])==cl and r['margin_rad']>=.18]
 if reference is not None:pool=[r for r in pool if np.hypot(r['alpha_over_pi']-reference[0],r['beta_over_pi']-reference[1])>=.10]
 if not pool:raise RuntimeError(f'No safe class {cl}')
 return max(pool,key=lambda r:r['margin_rad'])
def main():
 m=mod();prod={'alpha_over_pi':.75,'beta_over_pi':.90,**m.inv(.75*np.pi,.90*np.pi),'S_over_pi':1.65,'T':1.65*np.pi/2,'Omega':4/1.65};pi_records=line(m,1.65);zero_records=line(m,.825)
 c01=choose(pi_records,(0,1),(.75,.90));c10=choose(zero_records,(1,0));c00=choose(zero_records,(0,0))
 groups={'pi_matched':{'S_over_pi':1.65,'g':.08,'gamma1':.08,'periods':80,'discard_periods':20,'drives':{'nu11_production':prod,'nu01_same_period':c01}},'zero_matched':{'S_over_pi':.825,'g':.16,'gamma1':.16,'periods':160,'discard_periods':40,'drives':{'nu10_same_period':c10,'nu00_same_period':c00}}}
 for group in groups.values():
  for r in group['drives'].values():r['gT']=group['g']*r['T'];r['gamma1T']=group['gamma1']*r['T'];r['total_time']=group['periods']*r['T'];r['discard_time']=group['discard_periods']*r['T']
 p={'schema':'gate_a_v3_selected_controls_v1','selection_rule':'For each required class on its declared common-period line, maximize closed-chain bulk-gap margin subject to margin>=0.18 rad. The (0,1) candidate additionally remains >=0.10 in Euclidean alpha/pi,beta/pi distance from production.','groups':groups,'pairwise_matching_statement':'Within each group, T, Omega, gT, gamma1*T, total physical propagation time, discard time, detuning ratio grid and common product initial state are identical by construction. Across groups, g and gamma1 are rescaled to preserve gT and gamma1*T while periods are rescaled to preserve physical time.'}
 (OUT/'GATE_A_V3_SELECTED_CONTROLS.json').write_text(json.dumps(p,indent=2));print(json.dumps(p,indent=2))
if __name__=='__main__':main()

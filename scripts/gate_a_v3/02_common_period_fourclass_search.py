#!/usr/bin/env python3
"""Coarse-to-fine search for a single period line containing all four BDI classes."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

REPO=Path(__file__).resolve().parents[2];PREV=REPO/'scripts/gate_a_v3/01_iso_period_bdi_control_search.py';OUT=REPO/'results/gate_a_v3/control_search'
def load():
 s=importlib.util.spec_from_file_location('iso',PREV);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.KS=np.linspace(-np.pi,np.pi,1001,endpoint=False);return m
def scan_line(m,S,n=161):
 vals=[]
 for a in np.linspace(max(.04,S-.96),min(.96,S-.04),n):
  b=S-a;r=m.inv(a*np.pi,b*np.pi)
  if r['classified'] and r['margin_rad']>=.18:r.update({'alpha_over_pi':float(a),'beta_over_pi':float(b),'S_over_pi':float(S)});vals.append(r)
 out={}
 for r in vals:out.setdefault((r['nu0'],r['nupi']),[]).append(r)
 return {str(k):max(v,key=lambda x:x['margin_rad']) for k,v in out.items()},len(vals)
def main():
 m=load();target={'(0, 0)','(1, 0)','(0, 1)','(1, 1)'};candidates=[]
 for S in np.linspace(.16,1.84,85):
  best,n=scan_line(m,float(S));candidates.append({'S_over_pi':float(S),'class_keys':list(best),'safe_count':n,'best_by_class':best})
 full=[x for x in candidates if target.issubset(set(x['class_keys']))]
 # score: common line closest to production sum 1.65, then maximize minimum class margin
 for x in full:x['min_class_margin_rad']=min(x['best_by_class'][q]['margin_rad'] for q in target);x['production_sum_distance']=abs(x['S_over_pi']-1.65)
 chosen=min(full,key=lambda x:(x['production_sum_distance'],-x['min_class_margin_rad'])) if full else None
 payload={'schema':'gate_a_v3_common_period_fourclass_search_v1','safe_margin_threshold_rad':.18,'coarse_S_grid':85,'coarse_alpha_samples_per_line':161,'four_class_lines':full,'chosen_coarse_line':chosen,'all_line_summary':[{k:v for k,v in x.items() if k!='best_by_class'} for x in candidates]}
 (OUT/'COMMON_PERIOD_FOURCLASS_SEARCH.json').write_text(json.dumps(payload,indent=2));print(json.dumps({'n_four_class_lines':len(full),'chosen_coarse_line':chosen},indent=2))
if __name__=='__main__':main()

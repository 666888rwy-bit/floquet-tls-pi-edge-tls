#!/usr/bin/env python3
"""Read-only audit for the frozen Gate D1 N=4 nu_pi raw-weight screen."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'results/gate_d1/gate_d1.0__6d3a08047527'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def main():
    man=load(OUT/'MANIFEST.json'); checks={p:{'expected':h,'actual':sha(REPO/p),'matches':sha(REPO/p)==h} for p,h in man['sha256'].items()}
    if not all(v['matches'] for v in checks.values()):raise SystemExit('Manifest hash mismatch')
    records=[]
    for path in man['results']:
        rec=load(REPO/path); payload=dict(rec); observed=payload.pop('result_sha256_excluding_self')
        if hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=observed:raise SystemExit(f'Self hash mismatch: {path}')
        d=rec['task']; records.append({'id':d['id'],'nu0':d['nu0'],'nupi':d['nupi'],'alpha_over_pi':d['alpha_over_pi'],'beta_over_pi':d['beta_over_pi'],'T':d['T'],'margin_rad':d['bulk_margin_rad'],'W_r':rec['W_r'],'raw_peak':float(max(rec['raw_A_TLS']))})
    groups={(n0,npi):[x['W_r'] for x in records if x['nu0']==n0 and x['nupi']==npi] for n0 in [0,1] for npi in [0,1]}
    medians={f'nu{n0}{npi}':float(np.median(groups[(n0,npi)])) for n0 in [0,1] for npi in [0,1]}
    r0=medians['nu01']/medians['nu00'];r1=medians['nu11']/medians['nu10'];pi_values=groups[(0,1)]+groups[(1,1)];zero_values=groups[(0,0)]+groups[(1,0)]
    success={'nu0_0_median_ratio':r0,'nu0_1_median_ratio':r1,'min_nupi1_over_max_nupi0':min(pi_values)/max(zero_values),'frozen_condition_1_both_fixed_nu0_median_ratios_gt_10':bool(r0>10 and r1>10),'frozen_condition_2_all_nupi1_weights_exceed_all_nupi0_by_factor_10':bool(min(pi_values)/max(zero_values)>10)}
    success['screen_pass']=bool(success['frozen_condition_1_both_fixed_nu0_median_ratios_gt_10'] and success['frozen_condition_2_all_nupi1_weights_exceed_all_nupi0_by_factor_10'])
    payload={'schema':'gate_d1_n4_weight_audit_v1','manifest_integrity':checks,'records':records,'class_median_W_r':medians,'frozen_weight_screen':success,'interpretation':'This is a response-blind-selected N=4 stratified screen with common gT, gamma1T, common product state, 80-period readout and fixed ratio grid. It is a candidate-screen result, not a common-period four-class causal proof or universal nu_pi law.'}
    (OUT/'GATE_D1_N4_WEIGHT_AUDIT.json').write_text(json.dumps(payload,indent=2))
    fig,ax=plt.subplots(figsize=(7.0,4.2)); colors={0:'#d55e00',1:'#0072b2'};markers={0:'s',1:'o'}
    for n0 in [0,1]:
        for npi in [0,1]:
            vals=groups[(n0,npi)];x=npi+(-.12 if n0==0 else .12);ax.scatter([x]*len(vals),vals,s=72,color=colors[n0],marker=markers[n0],label=f'$\\nu_0={n0},\\nu_\\pi={npi}$')
    ax.set(xticks=[0,1],xticklabels=[r'$\nu_\pi=0$',r'$\nu_\pi=1$'],yscale='log',ylabel=r'raw integrated weight $W_r$',title='Gate D1: response-blind N=4 weight screen');handles,labels=ax.get_legend_handles_labels();by=dict(zip(labels,handles));ax.legend(by.values(),by.keys(),fontsize=8,ncol=2);ax.grid(axis='y',alpha=.25);fig.tight_layout();fig.savefig(OUT/'GATE_D1_N4_WEIGHT_SCREEN.png',dpi=260);plt.close(fig)
    print(json.dumps({'class_median_W_r':medians,'frozen_weight_screen':success},indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Read-only Gate A v3 audit and deterministic figures."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
REPO=Path(__file__).resolve().parents[2]
V3=REPO/'results/gate_a_v3/gate_a_v3.0__1b3dd5130c77'
V2=REPO/'results/gate_a_v2/gate_a_v2.0__00d3477cc81e'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def a(rec):return np.asarray(rec['raw_A_TLS'],float)
def r(rec):return np.asarray(rec.get('ratios',rec.get('detuning_ratios_omega_d_over_Omega_over_2')),float)
def norm(x):return x/max(float(np.linalg.norm(x)),1e-15)
def metric(num,den):
 x,y=a(num),a(den);rr=r(num);return {'W_numerator':float(np.trapezoid(x*x,rr)),'W_denominator':float(np.trapezoid(y*y,rr)),'directional_W_ratio':float(np.trapezoid(x*x,rr)/np.trapezoid(y*y,rr)),'shape_distance':float(np.linalg.norm(norm(x)-norm(y))),'raw_peak_ratio':float(max(x)/max(y))}
def main():
 man=load(V3/'MANIFEST.json');checks={p:{'expected':h,'actual':sha(REPO/p),'matches':sha(REPO/p)==h} for p,h in man['sha256'].items()}
 if not all(x['matches'] for x in checks.values()):raise SystemExit('v3 manifest hash mismatch')
 nu11=load(V2/'primary_controls/topological_obc_production_v2__m0.json');nu01=load(V3/'nu01_OBC_m0.json');nu10=load(V3/'nu10_OBC_m0.json');nu00=load(V3/'nu00_OBC_m0.json');ho=load(V2/'heldout_controls/heldout_topological_obc_v2__m0.json');hp=load(V3/'heldout_PBC_m0.json')
 pairs={'nu11_over_nu01':metric(nu11,nu01),'nu10_over_nu00':metric(nu10,nu00),'heldout_OBC_over_PBC':metric(ho,hp)}
 spatial={0:nu11};spatial.update({m:load(V3/f'production_spatial_m{m}.json') for m in range(1,6)})
 Wm={str(m):float(np.trapezoid(a(x)**2,r(x))) for m,x in spatial.items()};spatial_ratios={'W_m0_over_m1':Wm['0']/Wm['1'],'W_m0_over_m2':Wm['0']/Wm['2'],'W_m0_over_m3':Wm['0']/Wm['3'],'W_m0_over_m4':Wm['0']/Wm['4'],'W_m0_over_m5':Wm['0']/Wm['5']}
 conv={'baseline_s4_d20_v2':nu11}
 for tag in ['convergence_s2_d20','convergence_s8_d20','convergence_s4_d8','convergence_s4_d40']:conv[tag]=load(V3/f'{tag}.json')
 convergence={tag:{'shape_distance_to_baseline':float(np.linalg.norm(norm(a(rec))-norm(a(nu11)))),'raw_peak_ratio_to_baseline':float(max(a(rec))/max(a(nu11))),'W_ratio_to_baseline':float(np.trapezoid(a(rec)**2,r(rec))/np.trapezoid(a(nu11)**2,r(nu11)))} for tag,rec in conv.items() if tag!='baseline_s4_d20_v2'}
 # Qualitative test requested by frozen protocol; no retrospective threshold is inserted.
 d11_01=float(np.linalg.norm(norm(a(nu11))-norm(a(nu01))));d10_00=float(np.linalg.norm(norm(a(nu10))-norm(a(nu00))));cross=[float(np.linalg.norm(norm(a(x))-norm(a(y)))) for x in [nu11,nu01] for y in [nu10,nu00]]
 pi_pattern={'within_nupi1_D':d11_01,'within_nupi0_D':d10_00,'cross_nupi_D_values':cross,'cross_nupi_min':min(cross),'qualitative_support_for_pi_grouping':bool(d11_01<min(cross)),'note':'This is descriptive only: two matched-period pairs lie on different period lines, so it cannot by itself establish a universal pi-invariant response.'}
 payload={'schema':'gate_a_v3_audit_v1','v3_manifest_sha256':sha(V3/'MANIFEST.json'),'v3_integrity':checks,'source_sha256':{'nu11_v2':sha(V2/'primary_controls/topological_obc_production_v2__m0.json'),'heldout_obc_v2':sha(V2/'heldout_controls/heldout_topological_obc_v2__m0.json')},'directional_pairs':pairs,'spatial_W_r':Wm,'spatial_directional_ratios':spatial_ratios,'convergence':convergence,'pi_pattern':pi_pattern,'protocol_interpretation':'All directional ratios use the declared numerator/denominator order. V3 resolves the unequal-period v2 trivial control, but has no single common-period line containing all four BDI classes; its two pairwise matched lines preserve gT, gamma1T and physical propagation time within each pair.'}
 (V3/'GATE_A_V3_AUDIT.json').write_text(json.dumps(payload,indent=2))
 fig,axs=plt.subplots(2,2,figsize=(11,7.6),constrained_layout=True)
 for ax,items,title in [(axs[0,0],[(nu11,'(1,1) OBC'),(nu01,'(0,1) OBC')],r'matched $T$: $(1,1)$ vs $(0,1)$'),(axs[0,1],[(nu10,'(1,0) OBC'),(nu00,'(0,0) OBC')],r'matched $T$: $(1,0)$ vs $(0,0)$'),(axs[1,1],[(ho,'held-out (1,1) OBC'),(hp,'held-out same-drive PBC')],'held-out boundary control')]:
  for rec,label in items:ax.plot(r(rec),a(rec),marker='o',ms=3,label=label)
  ax.axvline(1,color='.5',ls=':',lw=.8);ax.set(title=title,xlabel=r'$\omega_d/(\Omega/2)$',ylabel=r'raw $A_{TLS}$');ax.grid(alpha=.25);ax.legend(fontsize=8)
 axs[1,0].plot(list(range(6)),[Wm[str(m)] for m in range(6)],marker='o',color='black');axs[1,0].set(title='production OBC spatial profile',xlabel='TLS contact site m',ylabel=r'$W_r(m)$');axs[1,0].grid(alpha=.25)
 fig.savefig(V3/'GATE_A_V3_CONTROLS.png',dpi=260);fig.savefig(V3/'GATE_A_V3_CONTROLS.pdf');plt.close(fig)
 fig,ax=plt.subplots(figsize=(6.8,3.8));tags=list(convergence);vals=[convergence[t]['shape_distance_to_baseline'] for t in tags];ax.bar(range(len(tags)),vals,color=['#0072b2','#009e73','#d55e00','#cc79a7']);ax.axhline(.10,color='black',ls='--',label='frozen acceptance 0.10');ax.set(xticks=range(len(tags)),xticklabels=['s2,d20','s8,d20','s4,d8','s4,d40'],ylabel='normalized-shape distance',title='production numerical convergence');ax.legend();fig.tight_layout();fig.savefig(V3/'GATE_A_V3_CONVERGENCE.png',dpi=260);plt.close(fig)
 print(json.dumps({'directional_pairs':pairs,'spatial_directional_ratios':spatial_ratios,'convergence':convergence,'pi_pattern':pi_pattern},indent=2))
if __name__=='__main__':main()

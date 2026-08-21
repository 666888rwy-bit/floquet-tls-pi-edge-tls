#!/usr/bin/env python3
"""Gate B1: diagnose why a pair-selected Floquet manifold misses the common state.

No response propagation is performed.  For each declared topological OBC drive
this script computes the exact Floquet basis, micromotion-averaged local B^(0),
the legacy near-pi local pair, and the weights |<phi_a|up_z^N>|^2.  It reports
retained weights for three *diagnostic* choices only:
  (i) local near-pi pair plus resonance-ranked channels,
 (ii) largest initial-support Floquet states,
(iii) local pair plus initial-support states.

The results are used to design a new, prospectively frozen Gate B2 manifold;
this script does not choose or validate a replacement model by itself.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import schur

REPO=Path(__file__).resolve().parents[2]
PROTOCOL=REPO/'protocols/gate_a_v2/gate_a_v2_protocol.json'
OUT=REPO/'results/gate_a_v2/gate_a_v2.0__00d3477cc81e/gate_b_diagnostics'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dkron(fs):
    x=np.array([[1.+0j]])
    for f in fs:x=np.kron(x,f)
    return x
def dop(o,j,n,i):return dkron([o if q==j else i for q in range(n)])
def prop(e,v,t):return (v*np.exp(-1j*e*t))@v.conj().T
def pierr(a,b):return float(abs(np.angle(np.exp(1j*(b-a-np.pi)))))

def diagnose(case,protocol):
    fixed=protocol['fixed_chain_TLS_model'];n=int(fixed['N_chain']);J=float(fixed['J']);h=float(fixed['h']);alpha=case['alpha_over_pi']*np.pi;beta=case['beta_over_pi']*np.pi;t1=beta/(2*J);t2=alpha/(2*h);T=t1+t2;omega=2*np.pi/T
    i2=np.eye(2,dtype=complex);x2=np.array([[0.,1.],[1.,0.]],complex);z2=np.diag([1.,-1.]).astype(complex);sm2=np.array([[0.,1.],[0.,0.]],complex)
    xs=[dop(x2,j,n,i2) for j in range(n)];zs=[dop(z2,j,n,i2) for j in range(n)];sm=dop(sm2,0,n,i2)
    links=[(j,j+1) for j in range(n-1)]
    h1=sum((-J*zs[a]@zs[b] for a,b in links),start=np.zeros((2**n,2**n),complex));h2=sum((-h*x for x in xs),start=np.zeros((2**n,2**n),complex));e1,v1=np.linalg.eigh(h1);e2,v2=np.linalg.eigh(h2);u1=prop(e1,v1,t1);u2=prop(e2,v2,t2);tri,V=schur(u2@u1,output='complex');ph=np.angle(np.diag(tri));eps=-ph/T
    B=np.zeros((2**n,2**n),complex);times=np.linspace(0,T,241)
    for k,t in enumerate(times):
        ev=prop(e1,v1,t) if t<=t1+1e-14 else prop(e2,v2,t-t1)@u1; modes=ev@V*np.exp(1j*eps*t)[None,:];B+=(.5 if k in (0,len(times)-1) else 1.)*(modes.conj().T@sm@modes)
    B*=(times[1]-times[0])/T
    candidates=[]
    for a in range(2**n):
        for b in range(a+1,2**n):
            err=pierr(ph[a],ph[b])
            if err<=.02:candidates.append((float(max(abs(B[a,b]),abs(B[b,a]))),err,a,b))
    candidates.sort(reverse=True);score,err,a,b=candidates[0];pair=[int(a),int(b)]
    ext=[]
    for q in range(2**n):
        if q in pair:continue
        w=float(sum(abs(B[q,p])**2+abs(B[p,q])**2 for p in pair));delta=min(abs(np.angle(np.exp(1j*(ph[q]-ph[p]))))/T for p in pair);ext.append((w/(delta**2+(.05*omega)**2),int(q),w,float(delta)))
    ext.sort(reverse=True);resonance=[q for _,q,_,_ in ext]
    psi=np.zeros(2**n,complex);psi[0]=1.;overlap=np.abs(V.conj().T@psi)**2;support=[int(q) for q in np.argsort(-overlap)]
    def uniq(seq):
        out=[]
        for q in seq:
            if q not in out:out.append(int(q))
        return out
    original={str(K):uniq(pair+resonance[:K-2]) for K in [2,4,8,16,32,64]}
    initial={str(K):support[:K] for K in [2,4,8,16,32,64]}
    hybrid={str(K):uniq(pair+support[:max(0,K-2)])[:K] for K in [2,4,8,16,32,64]}
    weight=lambda inds:float(np.sum(overlap[inds]))
    cumulative=np.cumsum(overlap[support])
    coverage={str(target):int(np.searchsorted(cumulative,target)+1) for target in [.5,.8,.9,.95,.99]}
    return {'case':case,'timing':{'T':T,'Omega':omega},'legacy_local_pair':{'indices':pair,'local_B0_score':score,'pi_mismatch_rad':err,'eligible_pair_count':len(candidates)},'top_initial_support':[{'index':int(q),'weight':float(overlap[q])} for q in support[:20]],'coverage_K_for_initial_weight':coverage,'retained_weight':{'legacy_resonance_ranked':{K:weight(v) for K,v in original.items()},'initial_support_ranked':{K:weight(v) for K,v in initial.items()},'hybrid_pair_plus_initial_support':{K:weight(v) for K,v in hybrid.items()}},'selected_indices':{'legacy_resonance_ranked':original,'initial_support_ranked':initial,'hybrid_pair_plus_initial_support':hybrid},'overlap_weight_by_numerical_index':overlap.tolist()}

def main():
    protocol=json.loads(PROTOCOL.read_text());cases=[c for c in protocol['controls'] if c['case_id'] in ['topological_obc_production_v2','heldout_topological_obc_v2']];OUT.mkdir(parents=True,exist_ok=True);results=[diagnose(c,protocol) for c in cases];payload={'schema':'gate_b_initial_support_diagnostic_v1','protocol_sha256':sha(PROTOCOL),'results':results};(OUT/'INITIAL_SUPPORT_DIAGNOSTIC.json').write_text(json.dumps(payload,indent=2))
    fig,ax=plt.subplots(figsize=(7.4,4.3))
    for r,color in zip(results,['black','#009e73']):
        weights=np.sort(np.asarray(r['overlap_weight_by_numerical_index']))[::-1];ax.semilogy(np.arange(1,len(weights)+1),weights,marker='o',ms=2.8,lw=1.2,color=color,label=r['case']['case_id'])
    ax.set(xlabel='Floquet eigenstate rank by initial-state overlap',ylabel=r'$|\langle\phi_a|\uparrow_z^{\otimes N}\rangle|^2$',title='Gate B: common-state support in Floquet basis');ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'INITIAL_SUPPORT_RANK.png',dpi=260);fig.savefig(OUT/'INITIAL_SUPPORT_RANK.pdf');print(OUT/'INITIAL_SUPPORT_DIAGNOSTIC.json')
if __name__=='__main__':main()

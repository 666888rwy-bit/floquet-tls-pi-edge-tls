#!/usr/bin/env python3
"""Search closed-chain BDI control points at the production period.

The line alpha/pi+beta/pi=1.65 preserves T, Omega, gT, gamma*T and the
80-period physical observation time when J=h=g=gamma=1,1,.08,.08 are held.
It does not calculate any TLS response.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'results/gate_a_v3/control_search'
OUT.mkdir(parents=True,exist_ok=True)
N_K=4001
KS=np.linspace(-np.pi,np.pi,N_K,endpoint=False)
W=np.array([[1.,1.],[1.,-1.]],complex)/np.sqrt(2)
S=1.65

def rot(ny,nz,theta):
 c,s=np.cos(theta),np.sin(theta);u=np.empty((ny.size,2,2),complex);u[:,0,0]=c-1j*s*nz;u[:,0,1]=-s*ny;u[:,1,0]=s*ny;u[:,1,1]=s*ny;u[:,1,1]=c+1j*s*nz;return u

def wind(u):
 uc=np.einsum('ij,...jk,kl->...il',W.conj().T,u,W,optimize=True);q=uc[:,0,1];wf=np.sum(np.angle(np.roll(q,-1)/q))/(2*np.pi);return int(np.rint(wf)),float(np.min(abs(q)))
def inv(a,b):
 u1=rot(np.sin(KS),np.cos(KS),b);u2=rot(np.zeros_like(KS),np.ones_like(KS),a);u1h=rot(np.sin(KS),np.cos(KS),b/2);u2h=rot(np.zeros_like(KS),np.ones_like(KS),a/2);ua=np.einsum('...ij,...jk,...kl->...il',u1h,u2,u1h,optimize=True);ub=np.einsum('...ij,...jk,...kl->...il',u2h,u1,u2h,optimize=True);wa,qa=wind(ua);wb,qb=wind(ub);u=np.einsum('...ij,...jk->...ik',u2,u1,optimize=True);phi=np.arccos(np.clip(np.real(np.trace(u,axis1=1,axis2=2))/2,-1,1));g0=float(np.min(phi));gp=float(np.min(abs(np.pi-phi)));n0=.5*(wa+wb);np0=.5*(wa-wb);ok=qa>1e-5 and qb>1e-5 and np.isclose(n0,round(n0)) and np.isclose(np0,round(np0));return {'nu0':int(round(n0)) if ok else None,'nupi':int(round(np0)) if ok else None,'classified':bool(ok),'wA':wa,'wB':wb,'gap0_rad':g0,'gappi_rad':gp,'margin_rad':min(g0,gp),'qmin_A':qa,'qmin_B':qb}
def main():
 records=[]
 for x in np.linspace(max(.04,S-.96),min(.96,S-.04),801):
  y=S-x;r=inv(x*np.pi,y*np.pi);r.update({'alpha_over_pi':float(x),'beta_over_pi':float(y),'T':float(S*np.pi/2),'Omega':float(4/S)});records.append(r)
 classes={}
 for r in records:
  if r['classified']:classes.setdefault(f"({r['nu0']},{r['nupi']})",[]).append(r)
 choices={k:max(v,key=lambda x:x['margin_rad']) for k,v in classes.items()}
 payload={'schema':'gate_a_v3_iso_period_bdi_search_v1','line':'alpha/pi+beta/pi=1.65','matching_statement':'J=h=1 fixes T=(alpha+beta)/2; holding g=gamma1=0.08 then fixes gT and gamma1*T, while 80 periods fixes physical observation time.','production':{'alpha_over_pi':.75,'beta_over_pi':.90,**inv(.75*np.pi,.90*np.pi)},'class_counts':{k:len(v) for k,v in classes.items()},'best_margin_candidate_by_class':choices,'records':records}
 (OUT/'ISO_PERIOD_BDI_SEARCH.json').write_text(json.dumps(payload,indent=2));print(json.dumps({'class_counts':payload['class_counts'],'best_margin_candidate_by_class':choices},indent=2))
if __name__=='__main__':main()

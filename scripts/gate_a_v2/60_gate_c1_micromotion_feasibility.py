#!/usr/bin/env python3
"""Gate C1: N=4 time-domain Fourier-micromotion feasibility benchmark."""
from __future__ import annotations
import hashlib, importlib.util, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.linalg import schur
from scipy.sparse import csr_matrix, eye, kron
from scipy.sparse.linalg import expm_multiply

REPO=Path(__file__).resolve().parents[2]
PROTOCOL=REPO/'protocols/gate_a_v2/gate_c1_micromotion_feasibility_protocol.json'
FULL_HELPER=REPO/'scripts/gate_a_v2/10_full_model_common_preparation.py'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc():return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def norm(a):return a/max(float(np.linalg.norm(a)),1e-15)
def dkron(fs):
 x=np.array([[1.+0j]])
 for f in fs:x=np.kron(x,f)
 return x
def dop(o,j,n,i):return dkron([o if q==j else i for q in range(n)])
def prop(e,v,t):return (v*np.exp(-1j*e*t))@v.conj().T
def pierr(a,b):return float(abs(np.angle(np.exp(1j*(b-a-np.pi)))))
def loadmod(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def liouv(H,C):
 d=H.shape[0];I=eye(d,format='csr',dtype=complex);cd=C.getH()@C
 return (-1j*(kron(I,H)-kron(H.T,I))+kron(C.conjugate(),C)-.5*kron(I,cd)-.5*kron(cd.T,I)).tocsr()
def expval(op,state,d):return np.trace(op.toarray()@state.reshape((d,d),order='F'))
def phasor(t,c,discard,omega):
 mask=t>=discard;tt=t[mask];cc=c[mask]-c[mask].mean();return float(abs(2*np.trapezoid(cc*np.exp(1j*omega*tt/2),tt)/(tt[-1]-tt[0])))
def sparse(a):return csr_matrix(np.asarray(a,dtype=complex))

def chain_data(p):
 f=p['full_model'];n=f['N_chain'];J=f['J'];h=f['h'];alpha=f['alpha_over_pi']*np.pi;beta=f['beta_over_pi']*np.pi;t1=beta/(2*J);t2=alpha/(2*h);T=t1+t2;omega=2*np.pi/T
 I=np.eye(2,dtype=complex);z=np.diag([1.,-1.]).astype(complex);x=np.array([[0.,1.],[1.,0.]],complex);sm=np.array([[0.,1.],[0.,0.]],complex);zs=[dop(z,j,n,I) for j in range(n)];xs=[dop(x,j,n,I) for j in range(n)];opsm=dop(sm,0,n,I)
 h1=sum((-J*zs[j]@zs[j+1] for j in range(n-1)),start=np.zeros((2**n,2**n),complex));h2=sum((-h*q for q in xs),start=np.zeros((2**n,2**n),complex));e1,v1=np.linalg.eigh(h1);e2,v2=np.linalg.eigh(h2);u1=prop(e1,v1,t1);u2=prop(e2,v2,t2);tri,V=schur(u2@u1,output='complex');phase=np.angle(np.diag(tri));eps=-phase/T
 def B(t):
  ev=prop(e1,v1,t) if t<=t1+1e-14 else prop(e2,v2,t-t1)@u1;modes=ev@V*np.exp(1j*eps*t)[None,:];return modes.conj().T@opsm@modes
 cand=[]
 for a in range(2**n):
  for b in range(a+1,2**n):
   err=pierr(phase[a],phase[b])
   if err<=.02:cand.append((float(max(abs(B(0)[a,b]),abs(B(0)[b,a]))),err,a,b))
 # Pair score must use B0, computed below; choose after B0 calculation.
 times=np.linspace(0,T,int(p['basis_and_initial_projection']['micromotion_quadrature_points']));Bt=np.asarray([B(t) for t in times]);weights=np.ones(len(times));weights[[0,-1]]=.5;Bn={}
 for nn in range(-2,3):Bn[nn]=np.tensordot(weights*np.exp(-1j*nn*omega*times),Bt,axes=(0,0))*(times[1]-times[0])/T
 b0=Bn[0];cand=[]
 for a in range(2**n):
  for b in range(a+1,2**n):
   err=pierr(phase[a],phase[b])
   if err<=.02:cand.append((float(max(abs(b0[a,b]),abs(b0[b,a]))),err,a,b))
 cand.sort(reverse=True);score,err,a,b=cand[0];pair=[int(a),int(b)]
 psi=np.zeros(2**n,complex);psi[0]=1.;support=[int(q) for q in np.argsort(-np.abs(V.conj().T@psi)**2)];selected=list(pair)
 for q in support:
  if q not in selected:selected.append(q)
  if len(selected)>=8:break
 ov=float(np.sum(np.abs((V[:,selected].conj().T@psi))**2));valid=[K for K in [4,6,8] if float(np.sum(np.abs((V[:,selected[:K]].conj().T@psi))**2))>=.90]
 if not valid:raise RuntimeError('Gate C K rule not satisfied through K=8')
 K=min(valid);inds=selected[:K];coeff=V[:,inds].conj().T@psi;pk=float(np.vdot(coeff,coeff).real)
 return {'n':n,'T':T,'omega':omega,'t1':t1,'t2':t2,'eps':eps[inds]-np.mean(eps[inds]),'V':V,'e1':e1,'v1':v1,'e2':e2,'v2':v2,'u1':u1,'sm':opsm,'indices':inds,'pair':pair,'pair_score':score,'pair_pi_error':err,'pK':pk,'c0':coeff/np.sqrt(pk),'Bn':{q:Bn[q][np.ix_(inds,inds)] for q in Bn},'K':K}

def b_exact(d,t):
 ev=prop(d['e1'],d['v1'],t) if t<=d['t1']+1e-14 else prop(d['e2'],d['v2'],t-d['t1'])@d['u1'];modes=ev@d['V']*np.exp(1j*(d['eps']+np.mean(d['eps']))*t)[None,:];return (modes.conj().T@d['sm']@modes)[np.ix_(d['indices'],d['indices'])]

def reduced_response(d,p,ratio,kind):
 K=d['K'];I=np.eye(K);z=np.diag([1.,-1.]).astype(complex);sm=np.array([[0.,1.],[0.,0.]],complex);g=p['full_model']['g'];gamma=p['full_model']['gamma1'];dim=2*K;obs=sparse(np.kron(I,sm));collapse=sparse(np.sqrt(gamma)*np.kron(I,sm));rho=np.outer(np.kron(d['c0'],np.array([1.,0.])),np.kron(d['c0'],np.array([1.,0.])).conj()).reshape(-1,order='F');base=np.kron(np.diag(d['eps']),np.eye(2))-.5*ratio*(d['omega']/2)*np.kron(I,z)
 def h_at(t):
  if kind=='static_M0':B=d['Bn'][0]
  elif kind=='Fourier_M1':B=sum(d['Bn'][q]*np.exp(1j*q*d['omega']*t) for q in [-1,0,1])
  elif kind=='Fourier_M2':B=sum(d['Bn'][q]*np.exp(1j*q*d['omega']*t) for q in [-2,-1,0,1,2])
  elif kind=='full_micromotion':B=b_exact(d,t)
  else:raise ValueError(kind)
  return sparse(base+g*(np.kron(B.conj().T,sm)+np.kron(B,sm.conj().T)))
 nper=p['common_readout']['periods'];samp=p['common_readout']['samples_per_half_step'];state=rho.copy();ts=[];cs=[];now=0.
 for _ in range(nper):
  for duration in [d['t1'],d['t2']]:
   dt=duration/samp
   for j in range(samp):
    ts.append(now);cs.append(expval(obs,state,dim));L=liouv(h_at(now+dt/2),collapse);state=expm_multiply(L*dt,state);now+=dt
 return phasor(np.asarray(ts),np.asarray(cs),p['common_readout']['discard_periods']*d['T'],d['omega'])

def main():
 p=json.loads(PROTOCOL.read_text())
 if p['status']!='prospectively_frozen_public_commit_required_for_run':raise SystemExit('Unexpected protocol status')
 if subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True).strip():raise SystemExit('Dirty tree; commit before Gate C1 run.')
 start=utc();d=chain_data(p);ratios=np.asarray(p['common_readout']['detuning_ratio_r'],float);fullh=loadmod(FULL_HELPER,'fullh');timing=fullh.make_timing(p['full_model']['alpha_over_pi'],p['full_model']['beta_over_pi'],p['full_model']['J'],p['full_model']['h']);sysfull=fullh.build_system(n_chain=4,jcoupling=1.,hfield=1.,boundary='OBC',contact=0,gamma1=p['full_model']['gamma1']);full=np.asarray([fullh.response_at_ratio(sysfull,timing,ratio=float(r),g=p['full_model']['g'],periods=p['common_readout']['periods'],samples_per_half=p['common_readout']['samples_per_half_step'],discard_periods=p['common_readout']['discard_periods']) for r in ratios])
 models={k:np.asarray([reduced_response(d,p,float(r),k) for r in ratios]) for k in ['static_M0','Fourier_M1','Fourier_M2','full_micromotion']};rows={}
 for name,a in models.items():rows[name]={'raw_A_TLS':a.tolist(),'normalized_shape':norm(a).tolist(),'epsilon_spec_vs_full':float(np.linalg.norm(norm(a)-norm(full))),'raw_peak_ratio_vs_full':float(max(a)/max(full)),'spectral_weight_ratio_vs_full':float(np.trapezoid(a*a,ratios)/np.trapezoid(full*full,ratios))}
 rows['Fourier_M1']['epsilon_vs_full_micromotion']=float(np.linalg.norm(norm(models['Fourier_M1'])-norm(models['full_micromotion'])));rows['Fourier_M2']['epsilon_vs_full_micromotion']=float(np.linalg.norm(norm(models['Fourier_M2'])-norm(models['full_micromotion'])));
 dec={'pK_pass':d['pK']>=.90,'m1_epsilon_pass':rows['Fourier_M1']['epsilon_spec_vs_full']<=.35,'m1_improvement_pass':rows['Fourier_M1']['epsilon_spec_vs_full']<=.75*rows['static_M0']['epsilon_spec_vs_full'],'m1_micro_pass':rows['Fourier_M1']['epsilon_vs_full_micromotion']<=.10,'m1_peak_pass':.5<=rows['Fourier_M1']['raw_peak_ratio_vs_full']<=2.};dec['pass_to_N6']=all(dec.values())
 out={'schema':'gate_c1_micromotion_feasibility_v1','protocol_sha256':sha(PROTOCOL),'script_sha256':sha(Path(__file__)),'git_commit':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),'run_started_utc':start,'run_finished_utc':utc(),'basis':{'K':d['K'],'indices':d['indices'],'p_K':d['pK'],'local_pair':d['pair'],'pair_B0_score':d['pair_score'],'pair_pi_mismatch_rad':d['pair_pi_error']},'ratios':ratios.tolist(),'full_exact_raw_A_TLS':full.tolist(),'models':rows,'decision':dec};out['result_sha256_excluding_self']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();dest=REPO/'results/gate_a_v2/gate_a_v2.0__00d3477cc81e/gate_c1/GATE_C1_MICROMOTION_FEASIBILITY.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(out,indent=2));print(dest)
if __name__=='__main__':main()

from pathlib import Path
import json
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix, eye, kron
from scipy.linalg import expm
from scipy.optimize import least_squares

OUT = Path(__file__).resolve().parents[1] / 'results' / 'generated'
OUT.mkdir(exist_ok=True)

# Same conventions and working point as the executed v3 channel/position notebook.
N = 4
J = h = 1.0
alpha_over_pi = 0.75
beta_over_pi = 0.90
g = 0.08
gamma1 = 0.08
alpha = alpha_over_pi*np.pi
beta = beta_over_pi*np.pi
T1 = beta/(2*J)
T2 = alpha/(2*h)
T = T1+T2
Omega = 2*np.pi/T
omega_d = Omega/2
periods = 80

I2 = csr_matrix(np.eye(2,dtype=complex))
X2 = csr_matrix(np.array([[0,1],[1,0]],dtype=complex))
Y2 = csr_matrix(np.array([[0,-1j],[1j,0]],dtype=complex))
Z2 = csr_matrix(np.diag([1.,-1.]).astype(complex))
SM2 = csr_matrix(np.array([[0,1],[0,0]],dtype=complex))

def kron_all(factors):
    out=csr_matrix([[1.+0j]])
    for item in factors:
        out=kron(out,item,format='csr')
    return out

def site_op(local,site,total):
    return kron_all([local if j==site else I2 for j in range(total)])

def liouvillian(H, collapse):
    d=H.shape[0]
    ident=eye(d,format='csr',dtype=complex)
    ans=-1j*(kron(ident,H,format='csr')-kron(H.T,ident,format='csr'))
    for c in collapse:
        cdc=c.getH()@c
        ans += kron(c.conjugate(),c,format='csr')-.5*kron(ident,cdc,format='csr')-.5*kron(cdc.T,ident,format='csr')
    return ans.tocsr()

def vec_density_zero(total):
    ket=np.zeros(2**total,dtype=complex); ket[0]=1
    return np.outer(ket,ket.conjugate()).reshape(-1,order='F')

def expect(operator,vec,d):
    rho=np.asarray(vec).reshape((d,d),order='F')
    return float(np.trace(operator.toarray()@rho).real)

n_total=N+1
d=2**n_total
x=[site_op(X2,i,n_total) for i in range(n_total)]
y=[site_op(Y2,i,n_total) for i in range(n_total)]
z=[site_op(Z2,i,n_total) for i in range(n_total)]
sm=[site_op(SM2,i,n_total) for i in range(n_total)]
hzz=sum((-J*(z[i]@z[i+1]) for i in range(N-1)),start=csr_matrix((d,d),dtype=complex))
hx=sum((-h*x[i] for i in range(N)),start=csr_matrix((d,d),dtype=complex))
hd=-.5*omega_d*z[N]
hed=g*(sm[0].getH()@sm[N]+sm[0]@sm[N].getH())
L1=liouvillian((hzz+hd+hed).tocsr(),[np.sqrt(gamma1)*sm[N]])
L2=liouvillian((hx+hd+hed).tocsr(),[np.sqrt(gamma1)*sm[N]])

started=time.perf_counter()
# Dense one-period channel is exact at N=4 and makes a long stroboscopic trace cheap.
F=expm(L2.toarray()*T2)@expm(L1.toarray()*T1)
print('channel construction seconds',time.perf_counter()-started)
evals, right=np.linalg.eig(F)
initial=vec_density_zero(n_total)
coeff=np.linalg.solve(right,initial)
readout=z[0].toarray().reshape(-1,order='F')
visibility=np.abs(readout.conjugate()@right*coeff)
phase_offset=np.angle(np.exp(1j*(np.angle(evals)-np.pi)))
# Select edge-visible conjugate pair within the same phase window used by the existing N=4 channel analysis.
selected={}
for sign in [1,-1]:
    candidates=np.where((sign*phase_offset>1e-8)&(sign*phase_offset<0.20*T))[0]
    selected[sign]=int(candidates[np.argmax(visibility[candidates])])
idx_plus,idx_minus=selected[1],selected[-1]
lambda_plus,lambda_minus=evals[idx_plus],evals[idx_minus]
# Pair symmetry diagnostic; use the average in magnitudes and absolute phase offsets.
r_pair=.5*(abs(lambda_plus)+abs(lambda_minus))
delta_pair=.5*(abs(phase_offset[idx_plus])+abs(phase_offset[idx_minus]))
tau_channel_periods=-1/np.log(r_pair)
tau_channel_time=T*tau_channel_periods
delta_omega_channel=delta_pair/T

# Raw, independently generated stroboscopic edge-magnetization trace.
vec=initial.copy()
n_values=np.arange(periods+1,dtype=float)
m=np.empty(periods+1)
for i in range(periods+1):
    m[i]=expect(z[0],vec,d)
    if i<periods:
        vec=F@vec

# Fit ansatz to the raw trace without using eigenvalue-derived seeds.
# m(n)=m_inf + A exp(-n/tau_periods) cos[(pi+delta)n+phi].
def model(params,n):
    m_inf,A,tau_p,delta,phi=params
    return m_inf+A*np.exp(-n/tau_p)*np.cos((np.pi+delta)*n+phi)

def residual(params,n,data):
    return model(params,n)-data

def multi_start_fit(start_index):
    n=n_values[start_index:]
    data=m[start_index:]
    # offset seed comes only from the late trace; all spectral seeds are deliberately generic.
    offset0=float(np.mean(m[-10:]))
    amplitude0=float(np.max(np.abs(data-offset0)))
    best=None
    for tau0 in [5.,10.,20.,35.,60.]:
        for delta0 in np.linspace(0.015,0.30,12):
            for phi0 in [0.,np.pi/2,np.pi, -np.pi/2]:
                initial_guess=np.array([offset0,amplitude0,tau0,delta0,phi0])
                ans=least_squares(residual,initial_guess,args=(n,data),bounds=([-1.1,-3.,1.0,0.,-2*np.pi],[1.1,3.,300.,0.6,2*np.pi]),max_nfev=20000,xtol=1e-13,ftol=1e-13,gtol=1e-13)
                rss=float(np.sum(ans.fun**2))
                if best is None or rss<best['rss']:
                    best={'params':ans.x,'rss':rss,'success':bool(ans.success),'nfev':int(ans.nfev),'n_start':int(start_index)}
    p=best['params']
    best.update({'m_inf':float(p[0]),'A':float(p[1]),'tau_periods':float(p[2]),'tau_time':float(p[2]*T),'delta_per_period':float(p[3]),'delta_omega':float(p[3]/T),'phi':float(p[4]),'rmse':float(np.sqrt(best['rss']/len(n))),'fit':model(p,n).tolist(),'n':n.tolist(),'data':data.tolist()})
    return best

fits=[multi_start_fit(s) for s in [0,4,8,12,16,20,24]]
# Pre-registered primary window: discard first 8 periods, which is independent of the
# channel eigenspectrum and matches the shortest production analysis discard window.
primary=next(item for item in fits if item['n_start']==8)

summary={'parameters':{'N':N,'g':g,'gamma1':gamma1,'T':T,'Omega':Omega,'omega_d':omega_d,'periods':periods},'channel':{'lambda_plus':[float(lambda_plus.real),float(lambda_plus.imag)],'lambda_minus':[float(lambda_minus.real),float(lambda_minus.imag)],'modulus_plus':float(abs(lambda_plus)),'modulus_minus':float(abs(lambda_minus)),'pair_modulus_mean':float(r_pair),'phase_offset_plus_per_period':float(phase_offset[idx_plus]),'phase_offset_minus_per_period':float(phase_offset[idx_minus]),'delta_per_period':float(delta_pair),'delta_omega':float(delta_omega_channel),'tau_periods':float(tau_channel_periods),'tau_time':float(tau_channel_time),'visibility_plus':float(visibility[idx_plus]),'visibility_minus':float(visibility[idx_minus]),'pair_conjugacy_error':float(abs(lambda_plus-np.conjugate(lambda_minus))),'selected_indices':{'plus':idx_plus,'minus':idx_minus}},'time_fit_primary':primary,'time_fit_window_sensitivity':fits,'relative_comparison':{'tau_fit_over_channel':float(primary['tau_periods']/tau_channel_periods),'delta_fit_over_channel':float(primary['delta_per_period']/delta_pair),'tau_relative_difference':float((primary['tau_periods']-tau_channel_periods)/tau_channel_periods),'delta_relative_difference':float((primary['delta_per_period']-delta_pair)/delta_pair)}}

# Paper figure: time trace + primary fit and channel-vs-time quantitative comparison.
plt.rcParams.update({'font.size':11,'axes.grid':True,'grid.alpha':.25})
fig,axes=plt.subplots(1,2,figsize=(12,4.2))
axes[0].plot(n_values,m,'o',ms=3,color='0.35',label=r'raw $m(n)=\langle Z_0\rangle$')
axes[0].plot(primary['n'],primary['fit'],'-',lw=2,color='C3',label='independent damped-cosine fit (n≥8)')
axes[0].axvspan(0,8,color='0.85',alpha=.7,label='discarded transient')
axes[0].set(xlabel='Floquet period $n$',ylabel=r'edge magnetization $\langle Z_0\rangle$',title='N=4 stroboscopic trace, g=γ₁=0.08')
axes[0].legend(fontsize=8)
labels=['channel','time-domain fit']
taus=[tau_channel_periods,primary['tau_periods']]
deltas=[delta_pair,primary['delta_per_period']]
pos=np.arange(2)
ax2=axes[1]
width=.36
ax2.bar(pos-width/2,taus,width,label=r'$\tau$ [periods]',color='C0')
ax2.set_ylabel(r'decay time $\tau/T$')
ax2.set_xticks(pos,labels)
ax2_t=ax2.twinx()
ax2_t.bar(pos+width/2,deltas,width,label=r'$|\delta|$ [rad/period]',color='C1')
ax2_t.set_ylabel(r'phase offset $|\delta|$ [rad/period]')
lines1,labs1=ax2.get_legend_handles_labels(); lines2,labs2=ax2_t.get_legend_handles_labels()
ax2.legend(lines1+lines2,labs1+labs2,loc='upper left',fontsize=8)
ax2.set_title('Channel–time-domain comparison')
fig.suptitle('N=4 exact Floquet channel validation',y=1.03)
fig.tight_layout()
fig.savefig(OUT/'C_N4_channel_time_validation.png',dpi=240,bbox_inches='tight')
plt.close(fig)

lines=['# C. N=4 channel → time-domain validation\n', '通道寿命采用正确的单位关系：若一周期本征值为 \(\lambda\)，则 \(|\lambda|^n=\exp[-nT/\tau]\)，故 \(\tau=-T/\ln|\lambda|\)，或以周期为单位 \(\tau/T=-1/\ln|\lambda|\)。\n', f'参数：N=4，g={g}，γ₁={gamma1}，ω_d=Ω/2，T={T:.12f}。\n', '\n## Channel pair\n', f'\(\lambda_+=({lambda_plus.real:.12f})+i({lambda_plus.imag:.12f})\)，\(\lambda_-=({lambda_minus.real:.12f})+i({lambda_minus.imag:.12f})\)。\n', f'\(|\lambda|={r_pair:.12f}\)，\(\tau_{{channel}}/T={tau_channel_periods:.6f}\)，\(\tau_{{channel}}={tau_channel_time:.6f}\)，\(|\delta_{{channel}}|={delta_pair:.9f}\) rad/period，\(\delta\\omega_{{channel}}={delta_omega_channel:.9f}\)。\n', '\n## Independent raw-trace fit\n', '对原始 stroboscopic \(\langle Z_0\rangle\) 做非线性拟合 \(m(n)=m_\infty+A\exp[-n/(\tau/T)]\cos[(\pi+\delta)n+\phi]\)。加入 \(m_\infty\) 是 CPTP 通道有非零非平衡稳态时的必要基线项；拟合初始化不使用通道本征值。主窗口预先固定为丢弃前 8 个周期。\n']
lines.append('| fit start | τ/T | δ [rad/period] | δω | RMSE | τ/τ_channel | δ/δ_channel |\n|---:|---:|---:|---:|---:|---:|---:|\n')
for f in fits:
    lines.append(f'| {f["n_start"]} | {f["tau_periods"]:.6f} | {f["delta_per_period"]:.9f} | {f["delta_omega"]:.9f} | {f["rmse"]:.6g} | {f["tau_periods"]/tau_channel_periods:.6f} | {f["delta_per_period"]/delta_pair:.6f} |\n')
lines += [f'\n主窗口（n≥8）的比较：\(\tau_{{fit}}/\tau_{{channel}}={primary["tau_periods"]/tau_channel_periods:.6f}\)，\(\delta_{{fit}}/\delta_{{channel}}={primary["delta_per_period"]/delta_pair:.6f}\)。\n', '\n窗口敏感性用于诊断早期多模瞬态：只有当主窗口与相邻窗口均保持合理一致时，才可写成通道对时域衰减和劈裂的定量预测。\n']
(OUT/'C_N4_channel_time_validation_results.md').write_text(''.join(lines),encoding='utf-8')
(OUT/'C_N4_channel_time_validation_results.json').write_text(json.dumps(summary, indent=2, default=lambda value: value.tolist() if isinstance(value, np.ndarray) else float(value) if isinstance(value, np.floating) else int(value) if isinstance(value, np.integer) else str(value)),encoding='utf-8')
print(OUT/'C_N4_channel_time_validation_results.md')
print(OUT/'C_N4_channel_time_validation.png')

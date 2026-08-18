import numpy as np
from scipy.sparse import csr_matrix, eye, kron
from scipy.sparse.linalg import expm_multiply
from pathlib import Path

I2 = csr_matrix(np.eye(2, dtype=complex))
X2 = csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex))
Y2 = csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex))
Z2 = csr_matrix(np.diag([1.0, -1.0]).astype(complex))
SM2 = csr_matrix(np.array([[0, 1], [0, 0]], dtype=complex))

def kron_all(factors):
    out = csr_matrix([[1.0 + 0.0j]])
    for factor in factors:
        out = kron(out, factor, format='csr')
    return out

def op(local, site, total):
    return kron_all([local if j == site else I2 for j in range(total)])

def L(H, cs):
    D = H.shape[0]
    ident = eye(D, format='csr', dtype=complex)
    ans = -1j * (kron(ident, H, format='csr') - kron(H.T, ident, format='csr'))
    for c in cs:
        cdc = c.getH() @ c
        ans = ans + kron(c.conjugate(), c, format='csr') - .5*kron(ident, cdc, format='csr') - .5*kron(cdc.T, ident, format='csr')
    return ans.tocsr()

def expval(O, vec, d):
    return float(np.trace(O.toarray() @ np.asarray(vec).reshape((d,d),order='F')).real)

def phasor(t, s, omega, discard):
    mask = t >= discard
    t, s = t[mask], np.asarray(s)[mask]
    s = s-s.mean()
    return 2*np.trapezoid(s*np.exp(1j*omega*t/2),t)/(t[-1]-t[0])

N=6; J=h=1.; alpha=.75*np.pi; beta=.90*np.pi
T1=beta/(2*J); T2=alpha/(2*h); T=T1+T2; Omega=2*np.pi/T
g=.08; gamma=.08; omega=Omega/2; periods=80; samples=4
total=N+1; d=2**total
xs=[op(X2,j,total) for j in range(total)]
ys=[op(Y2,j,total) for j in range(total)]
zs=[op(Z2,j,total) for j in range(total)]
sms=[op(SM2,j,total) for j in range(total)]
hzz=sum((-J*(zs[j]@zs[j+1]) for j in range(N-1)), start=csr_matrix((d,d),dtype=complex))
hx=sum((-h*xs[j] for j in range(N)), start=csr_matrix((d,d),dtype=complex))
hd=-.5*omega*zs[N]
hed=g*(sms[0].getH()@sms[N] + sms[0]@sms[N].getH())
l1=L((hzz+hd+hed).tocsr(),[np.sqrt(gamma)*sms[N]])
l2=L((hx+hd+hed).tocsr(),[np.sqrt(gamma)*sms[N]])
bits=np.zeros(d,complex); bits[0]=1.; vec=np.outer(bits,bits.conjugate()).reshape(-1,order='F')
edge=[]; tx=[]; ty=[]; pe=[]; times=[]; strobe=[]; time=0.
Pexc=.5*(eye(d,format='csr')-zs[N])
for _ in range(periods):
    strobe.append(expval(zs[0],vec,d))
    a=expm_multiply(l1,vec,start=0,stop=T1,num=samples+1,endpoint=True)
    for sample in range(samples):
        times.append(time+sample*T1/samples); edge.append(expval(zs[0],a[sample],d)); tx.append(expval(xs[N],a[sample],d)); ty.append(expval(ys[N],a[sample],d)); pe.append(expval(Pexc,a[sample],d))
    vec=a[-1]; time +=T1
    a=expm_multiply(l2,vec,start=0,stop=T2,num=samples+1,endpoint=True)
    for sample in range(samples):
        times.append(time+sample*T2/samples); edge.append(expval(zs[0],a[sample],d)); tx.append(expval(xs[N],a[sample],d)); ty.append(expval(ys[N],a[sample],d)); pe.append(expval(Pexc,a[sample],d))
    vec=a[-1]; time +=T2
strobe.append(expval(zs[0],vec,d))
times=np.array(times); edge=np.array(edge); tls=.5*(np.array(tx)+1j*np.array(ty)); pe=np.array(pe)
mask=times>=20*T
strobe_start = int(np.floor(20 / periods * len(strobe)))
late_strobe = np.asarray(strobe[strobe_start:])
mpi_value = float(abs(np.mean(((-1.0) ** np.arange(len(late_strobe))) * late_strobe)))
metrics={
    'A_edge_d20': float(abs(phasor(times, edge, Omega, 20*T))),
    'A_tls_transverse_d20': float(abs(phasor(times, tls, Omega, 20*T))),
    'phase_tls_minus_edge_d20': float(np.angle(phasor(times, tls, Omega, 20*T) / phasor(times, edge, Omega, 20*T))),
    'tls_emission_d20': float(gamma * pe[mask].mean()),
    'Mpi_edge_strobe_d20': mpi_value,
}
with np.load(str(Path(__file__).resolve().parents[1] / 'data' / 'checkpoints' / 'floquet_tls_N6_g_frequency_checkpoint.npz'),allow_pickle=False) as ck:
    gi=int(np.where(np.isclose(ck['g_values'],g))[0][0]); fi=int(np.where(np.isclose(ck['omega_ratios'],1.0))[0][0])
    reference={k:float(ck[k][gi,fi]) for k in metrics}
print('parameters',{'N':N,'g':g,'gamma':gamma,'omega_ratio':omega/(Omega/2),'T':T,'Omega':Omega})
for k in metrics:
    value=metrics[k]; ref=reference[k]
    print(k,{'reproduced':value,'checkpoint':ref,'absolute_error':abs(value-ref),'relative_error':abs(value-ref)/max(abs(ref),1e-15)})

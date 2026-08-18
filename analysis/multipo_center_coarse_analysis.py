from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'checkpoints'
OUT = ROOT / 'results' / 'generated'
OUT.mkdir(exist_ok=True)
B=np.asarray([.27267967049286684,.01359485,.00080765])
def vertex(x,y,i):
 if i<=0 or i>=len(x)-1:return float(x[i])
 q=np.polyfit(x[i-1:i+2],y[i-1:i+2],2);xx=-q[1]/(2*q[0])
 return float(xx if x[i-1]<=xx<=x[i+1] else x[i])
def allpeaks(x,y):
 p,_=find_peaks(y,prominence=max(1e-10,.04*np.ptp(y)),distance=2)
 return p
def innerpair(x,y):
 p=allpeaks(x,y);L=[i for i in p if .75<=x[i]<1];R=[i for i in p if 1<x[i]<=1.30]
 if not L or not R:return None,p
 il=max(L,key=lambda i:x[i]);ir=min(R,key=lambda i:x[i]);a,b=vertex(x,y,il),vertex(x,y,ir)
 return {'left':a,'right':b,'midpoint':.5*(a+b),'half':.5*(b-a)},p
with np.load(DATA/'multipo_center_coarse_checkpoint.npz',allow_pickle=False) as d:
 sites=np.asarray(d['sites'],int);gs=np.asarray(d['g_values'],float);r=np.asarray(d['ratios'],float);ws=np.asarray(d['windows'],int);data={(int(site),int(w)):np.asarray(d[f'A_tls_d{int(w):02d}'][i]) for i,site in enumerate(sites) for w in ws}
with np.load(str(Path(__file__).resolve().parents[1] / 'data' / 'checkpoints' / 'floquet_tls_N6_position_frequency_checkpoint.npz'),allow_pickle=False) as d:
 r0=np.asarray(d['ratios'],float); ref={(0,int(w)):np.asarray(d[f'A_tls_d{int(w):02d}'][0]) for w in ws}
rows=[]
for site in [0,1,2]:
 g=.08 if site==0 else float(gs[np.where(sites==site)[0][0]])
 for w in ws:
  x=r0 if site==0 else r;y=ref[(0,int(w))] if site==0 else data[(site,int(w))];pr,ps=innerpair(x,y)
  rows.append({'site':site,'g':g,'geff':g*B[site],'window':int(w),'pair':pr,'peaks':ps.tolist(),'maxratio':float(x[np.argmax(y)]),'maxval':float(y.max())})
plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.25})
fig,axes=plt.subplots(2,1,figsize=(8.5,6.5),sharex=True)
colors={0:'C0',1:'C1',2:'C2'}
for ax,w in zip(axes,ws):
 for site in [0,1,2]:
  x=r0 if site==0 else r;y=ref[(0,int(w))] if site==0 else data[(site,int(w))]
  ax.plot(x,y/y.max(),'o-',ms=3,color=colors[site],label=fr'$m={site}$, $g={(.08 if site==0 else gs[np.where(sites==site)[0][0]]):.3g}$')
  p=allpeaks(x,y)
  ax.plot(x[p],(y/y.max())[p],'x',ms=8,mew=2,color=colors[site])
 ax.axvline(1,color='0.4',ls=':');ax.set(ylabel='normalized TLS transverse response',title=f'discard {w}T')
 ax.legend(fontsize=8)
axes[-1].set(xlabel=r'$\omega_d/(\Omega/2)$')
fig.suptitle(r'Center-$|g_m|$ coarse scan: equal $|g_m|=0.02181$, but widely different bare $g$',y=.98)
fig.tight_layout()
fig.savefig(OUT/'multipo_center_coarse_spectra.png',dpi=220,bbox_inches='tight');plt.close(fig)
lines=['# 多位置中心有效耦合粗扫描：峰对诊断\n','三处均瞄准相同 \(|g_m|=0.02181437\)，但所需 bare \(g\) 分别为 0.08、1.6046、27.0097。m=0 为已有 80-period/4-sample 生产参考；m=1、2 为 40-period/2-sample 粗扫描，仅用于决定是否值得进入高分辨生产计算。\n','| m | g | \|g_m\| | discard | peak pair | midpoint | half split (ratio) | all detected peaks | global max ratio |\n|---:|---:|---:|---:|---|---:|---:|---|---:|\n']
for rr in rows:
 p=rr['pair'];ptext='—' if p is None else f'({p["left"]:.4f},{p["right"]:.4f})';mid='—' if p is None else f'{p["midpoint"]:.4f}';half='—' if p is None else f'{p["half"]:.4f}'
 lines.append(f'| {rr["site"]} | {rr["g"]:.6g} | {rr["geff"]:.8f} | {rr["window"]}T | {ptext} | {mid} | {half} | {rr["peaks"]} | {rr["maxratio"]:.3f} |\n')
lines.append('\n结论判据：若 m=1、2 也在共振附近、且跨窗口均给出相同的双峰半劈裂，则可继续在多个有效耦合点加密扫描并进行真正 collapse。若峰对中心大幅离开共振、随窗口消失或高裸耦合产生多峰结构，则 \(g|B_{0\pi}(m)|\) 的单参数有效模型在该位置不适用，完整坍缩图不应强行制造。\n')
(OUT/'multipo_center_coarse_analysis.md').write_text(''.join(lines),encoding='utf-8')
print(OUT/'multipo_center_coarse_analysis.md')
print(OUT/'multipo_center_coarse_spectra.png')

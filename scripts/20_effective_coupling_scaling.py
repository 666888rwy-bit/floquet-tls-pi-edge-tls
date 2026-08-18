from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

SRC = Path(__file__).resolve().parents[1] / 'data' / 'checkpoints'
OUT = Path(__file__).resolve().parents[1] / 'results' / 'reproduced'
OUT.mkdir(exist_ok=True)

B0PI_EDGE = 0.27267967049286684  # selected N=6 m=0 dressed 0-pi matrix element


def quadratic_vertex(x, y, idx):
    if idx <= 0 or idx >= len(x)-1:
        return float(x[idx]), float(y[idx])
    coef = np.polyfit(x[idx-1:idx+2], y[idx-1:idx+2], 2)
    xv = -coef[1]/(2*coef[0])
    if not x[idx-1] <= xv <= x[idx+1]:
        xv = x[idx]
    return float(xv), float(np.polyval(coef, xv))


def inner_peak_pair(x, y, center=1.0):
    span = float(np.ptp(y))
    candidates, _ = find_peaks(y, prominence=max(1e-8,0.04*span), distance=3)
    left = [i for i in candidates if 0.86 <= x[i] < center]
    right = [i for i in candidates if center < x[i] <= 1.24]
    if not left or not right:
        return None
    i_left = max(left, key=lambda i: x[i])
    i_right = min(right, key=lambda i: x[i])
    l = quadratic_vertex(x,y,i_left)
    r = quadratic_vertex(x,y,i_right)
    return {'left':l,'right':r,'midpoint':.5*(l[0]+r[0]),'half_split_ratio':.5*(r[0]-l[0])}

with np.load(SRC/'floquet_tls_N6_g_frequency_checkpoint.npz',allow_pickle=False) as d:
    g_all=np.asarray(d['g_values'],float)
    ratios=np.asarray(d['omega_ratios'],float)
    windows=np.asarray(d['discard_windows'],int)
    omega_half=float(d['metadata_Omega'])/2
    response={int(w):np.asarray(d[f'A_tls_transverse_d{w:02d}'],float) for w in windows}

rows=[]
for i,g in enumerate(g_all):
    half=[]; mid=[]
    for w in windows:
        pair=inner_peak_pair(ratios,response[int(w)][i])
        if pair is not None:
            half.append(pair['half_split_ratio']*omega_half)
            mid.append(pair['midpoint'])
    if len(half)==len(windows):
        half=np.asarray(half); mid=np.asarray(mid)
        cv=float(np.std(half,ddof=1)/np.mean(half))
        accepted=bool(abs(np.mean(mid)-1.0)<=.04 and cv<=.10)
        rows.append({'g':float(g),'g_eff':float(g*B0PI_EDGE),'resolved_windows':len(half),'half_split':float(np.mean(half)),'half_split_window_std':float(np.std(half,ddof=1)),'full_split':float(2*np.mean(half)),'full_split_window_std':float(2*np.std(half,ddof=1)),'midpoint':float(np.mean(mid)),'midpoint_std':float(np.std(mid,ddof=1)),'cv':cv,'accepted':accepted})
    else:
        rows.append({'g':float(g),'g_eff':float(g*B0PI_EDGE),'resolved_windows':len(half),'half_split':None,'half_split_window_std':None,'full_split':None,'full_split_window_std':None,'midpoint':None,'midpoint_std':None,'cv':None,'accepted':False})

accepted=[r for r in rows if r['accepted']]
x=np.array([r['g_eff'] for r in accepted])
y=np.array([r['full_split'] for r in accepted])
yerr=np.array([r['full_split_window_std'] for r in accepted])
coef=np.polyfit(x,y,1)
pred=np.polyval(coef,x)
r2=float(1-np.sum((y-pred)**2)/np.sum((y-y.mean())**2))
# Weighted/unweighted linear fits have almost identical purposes here; provide both.
weights=1/np.maximum(yerr,1e-10)
coef_w=np.polyfit(x,y,1,w=weights)
pred_w=np.polyval(coef_w,x)
# origin-constrained slope reveals whether data support true perturbative proportionality.
slope0=float(np.dot(x,y)/np.dot(x,x))
r2_origin=float(1-np.sum((y-slope0*x)**2)/np.sum((y-y.mean())**2))

output={'B0pi_edge':B0PI_EDGE,'omega_half':omega_half,'rows':rows,'accepted_fit':{'full_split_vs_g_eff':{'slope':float(coef[0]),'intercept':float(coef[1]),'R2':r2,'weighted_slope':float(coef_w[0]),'weighted_intercept':float(coef_w[1]),'origin_constrained_slope':slope0,'origin_constrained_R2':r2_origin},'half_split_vs_g_eff':{'slope':float(coef[0]/2),'intercept':float(coef[1]/2)}}}

plt.rcParams.update({'font.size':11,'axes.grid':True,'grid.alpha':.25})
fig,axes=plt.subplots(1,2,figsize=(11.5,4.2))
for r in rows:
    if r['full_split'] is None:
        axes[0].scatter(r['g_eff'],0,marker='x',color='0.6',label='unresolved/excluded' if r['g']==0.02 else None)
        continue
    style='o' if r['accepted'] else 's'
    color='C0' if r['accepted'] else 'C1'
    axes[0].errorbar(r['g_eff'],r['full_split'],yerr=r['full_split_window_std'],fmt=style,color=color,capsize=3,label='accepted, 3 windows' if r['g']==accepted[0]['g'] else ('resolved but excluded' if not r['accepted'] else None))
line=np.linspace(x.min()*0.9,x.max()*1.08,300)
axes[0].plot(line,np.polyval(coef,line),'k--',label=fr'free intercept: $\Delta\omega={coef[0]:.3f}|g_m|{coef[1]:+.4f}$, $R^2={r2:.4f}$')
axes[0].plot(line,slope0*line,':',color='0.35',label=fr'forced origin: $\Delta\omega={slope0:.3f}|g_m|$, $R^2={r2_origin:.4f}$')
axes[0].set(xlabel=r'$|g_m|=g|B_{0\pi}(m=0)|$',ylabel=r'full response splitting $\Delta\omega_{\rm response}$',title='N=6 TLS response doublet')
axes[0].legend(fontsize=8)
# Second panel documents that effective coupling is a rescaled bare coupling at fixed contact.
profile=np.array([.27267967049286684,.01359485,.00080765,.00080765,.01359485,.27267967049286684])
axes[1].semilogy(np.arange(6),profile/profile.max(),'o-',label=r'$|B_{0\pi}(m)|/|B_{0\pi}(0)|$')
axes[1].set(xlabel='contact site $m$',ylabel='normalized dressed matrix element',xticks=np.arange(6),title=r'N=6 selected $0$–$\pi$ matrix-element profile')
axes[1].legend()
fig.suptitle('Response-splitting scaling with local effective coupling',y=1.03)
fig.tight_layout()
fig.savefig(OUT/'B_response_splitting_vs_geff.png',dpi=240,bbox_inches='tight')
plt.close(fig)

lines=[
    '# B. 响应双峰劈裂对有效矩阵元的标度\n',
    fr'采用已选 N=6 \(0\)–\(\pi\) 对的边界矩阵元 \(|B_{{0\pi}}(0)|={B0PI_EDGE:.12f}\)。生产频率扫描中 TLS 始终接触于 \(m=0\)，因此 \(|g_m|=g|B_{{0\pi}}(0)|\)。纵轴为全劈裂 \(\Delta\omega_{{response}}=2\delta\omega\)；每个误差条是三个舍弃窗口的标准差，表示窗口系统敏感性。' + '\n',
]
lines.append('| g | |g_m| | resolved windows | full splitting | window s.d. | midpoint | accepted |\n|---:|---:|---:|---:|---:|---:|---:|\n')
for r in rows:
    fmt=lambda v: '—' if v is None else f'{v:.6f}'
    lines.append(f'| {r["g"]:.3f} | {r["g_eff"]:.8f} | {r["resolved_windows"]} | {fmt(r["full_split"])} | {fmt(r["full_split_window_std"])} | {fmt(r["midpoint"])} | {r["accepted"]} |\n')
fit=output['accepted_fit']['full_split_vs_g_eff']
lines += [
    '\n' + fr'接受点的自由截距拟合：\(\Delta\omega_{{response}}=({fit["slope"]:.6f})|g_m|{fit["intercept"]:+.6f}\)，\(R^2={fit["R2"]:.6f}\)。强制过原点拟合给出斜率 {fit["origin_constrained_slope"]:.6f}，\(R^2={fit["origin_constrained_R2"]:.6f}\)。' + '\n',
    '\n' + r'解释：在固定接触点 \(m=0\) 的现有数据中，横轴从 \(g\) 替换为 \(g|B_{0\pi}(0)|\) 是确定的物理重标定，因而不会独立改变线性相关系数。其价值在于使横轴成为局域有效耦合并可与未来的多位置数据直接比较。非零截距反映现有频率网格和线宽下的解析阈值，不能被写成严格的 \(g\to0\) 微扰定律。要检验真正的 \(m\)-collapse，下一步需在至少两个内侧接触点重复可分辨的 \(g\)–频率扫描。' + '\n',
]
(OUT/'B_geff_scaling_results.md').write_text(''.join(lines),encoding='utf-8')
(OUT/'B_geff_scaling_results.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
print(OUT/'B_geff_scaling_results.md')
print(OUT/'B_response_splitting_vs_geff.png')

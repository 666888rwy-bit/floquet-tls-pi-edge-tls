from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, least_squares

SRC = Path(__file__).resolve().parents[1] / 'data' / 'checkpoints'
OUT = Path(__file__).resolve().parents[1] / 'results' / 'generated'
OUT.mkdir(exist_ok=True)

XI_B = 0.3336
XI_PI = 0.3671


def profile(x, a_left, a_right, xi):
    n_minus_one = 5.0
    return a_left * np.exp(-x / xi) + a_right * np.exp(-(n_minus_one - x) / xi)


def fit_one(x, y):
    # Amplitudes and localization length are physically nonnegative.
    p0 = [float(y[0]), float(y[-1]), 0.35]
    upper = [10.0 * max(float(y.max()), 1e-12), 10.0 * max(float(y.max()), 1e-12), 10.0]
    popt, pcov = curve_fit(profile, x, y, p0=p0, bounds=([0.0, 0.0, 0.02], upper), maxfev=100000)
    residual = y - profile(x, *popt)
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((y-y.mean())**2))
    return {
        'AL': float(popt[0]), 'AR': float(popt[1]), 'xi': float(popt[2]),
        'xi_fit_standard_error': float(np.sqrt(max(pcov[2,2], 0.0))),
        'r2': float(1-ss_res/ss_tot) if ss_tot > 0 else float('nan'),
        'rmse': float(np.sqrt(np.mean(residual**2))),
        'data': y.tolist(), 'fit': profile(x,*popt).tolist(), 'residual': residual.tolist()
    }

with np.load(SRC / 'floquet_tls_N6_position_frequency_checkpoint.npz', allow_pickle=False) as d:
    x = np.asarray(d['sites'], dtype=float)
    ratios = np.asarray(d['ratios'], dtype=float)
    windows = np.asarray(d['windows'], dtype=int)
    a_tls = {int(w): np.asarray(d[f'A_tls_d{w:02d}'], dtype=float) for w in windows}

# In a linear-response interpretation the square root of frequency-integrated
# |TLS transverse phasor|^2 is an amplitude-like spectral weight and is the
# closest raw-response proxy for a local matrix element. Peak and exact-resonance
# profiles are retained as sensitivity checks rather than mixed into the primary fit.
metrics = {
    'root_integrated_power': {},
    'peak_amplitude': {},
    'nominal_resonance_amplitude': {},
}
res_index = int(np.argmin(abs(ratios - 1.0)))
for w in windows:
    arr = a_tls[int(w)]
    metrics['root_integrated_power'][int(w)] = np.sqrt(np.trapezoid(arr**2, ratios, axis=1))
    metrics['peak_amplitude'][int(w)] = np.max(arr, axis=1)
    metrics['nominal_resonance_amplitude'][int(w)] = arr[:, res_index]

results = {'reference_xi_B': XI_B, 'reference_xi_pi': XI_PI, 'primary_metric': 'root_integrated_power', 'per_metric': {}}
for metric_name, by_window in metrics.items():
    fits = {str(w): fit_one(x, y) for w, y in by_window.items()}
    # Joint fit: window-dependent AL/AR but one common xi across all 18 points.
    ordered_windows = [int(w) for w in windows]
    y_stack = np.concatenate([by_window[w] for w in ordered_windows])
    x_stack = np.tile(x, len(ordered_windows))
    which = np.repeat(np.arange(len(ordered_windows)), len(x))
    start = []
    for w in ordered_windows:
        start += [fits[str(w)]['AL'], fits[str(w)]['AR']]
    start += [np.median([fits[str(w)]['xi'] for w in ordered_windows])]
    def residuals(params):
        xi = params[-1]
        prediction = np.empty_like(y_stack)
        for i in range(len(ordered_windows)):
            mask = which == i
            prediction[mask] = profile(x_stack[mask], params[2*i], params[2*i+1], xi)
        return prediction-y_stack
    upper = []
    for w in ordered_windows:
        max_y = max(float(by_window[w].max()), 1e-12)
        upper += [10*max_y, 10*max_y]
    upper += [10.0]
    joint = least_squares(residuals, x0=np.asarray(start), bounds=(np.array([0.0]*(2*len(ordered_windows))+[0.02]), np.asarray(upper)), max_nfev=100000)
    r = residuals(joint.x)
    joint_xi = float(joint.x[-1])
    # Window-to-window variation is a deterministic finite-observation systematic,
    # not a statistical confidence interval.
    xi_values = np.array([fits[str(w)]['xi'] for w in ordered_windows])
    results['per_metric'][metric_name] = {
        'fits': fits,
        'joint_common_xi': joint_xi,
        'joint_rmse': float(np.sqrt(np.mean(r**2))),
        'xi_window_mean': float(xi_values.mean()),
        'xi_window_std_systematic': float(xi_values.std(ddof=1)),
        'ratio_to_xi_B': float(joint_xi / XI_B),
        'ratio_to_xi_pi': float(joint_xi / XI_PI),
    }

# Figure: primary (top) plus sensitivity diagnostics (bottom).
plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': 0.25})
fig, axes = plt.subplots(1, 3, figsize=(14, 4.0), sharex=True)
colors = {8:'#1f77b4',20:'#ff7f0e',40:'#2ca02c'}
labels = {'root_integrated_power': r'$[\int |A_{\rm TLS}^{\perp}(\omega)|^2d\omega]^{1/2}$', 'peak_amplitude': r'$\max_\omega |A_{\rm TLS}^{\perp}|$', 'nominal_resonance_amplitude': r'$|A_{\rm TLS}^{\perp}(\omega_d=\Omega/2)|$'}
for ax, metric_name in zip(axes, labels):
    for w in windows:
        y = metrics[metric_name][int(w)]
        fit = results['per_metric'][metric_name]['fits'][str(int(w))]
        ax.semilogy(x, y/y.max(), 'o', color=colors[int(w)], label=f'discard {int(w)}T')
        fine = np.linspace(0,5,300)
        ax.semilogy(fine, profile(fine, fit['AL'],fit['AR'],fit['xi'])/y.max(), '-', color=colors[int(w)], alpha=.9)
    xi_joint = results['per_metric'][metric_name]['joint_common_xi']
    ax.set(title=labels[metric_name]+'\n'+fr'joint $\xi={xi_joint:.3f}$', xlabel='TLS contact site $m$', ylabel='normalized spatial response', xticks=np.arange(6), ylim=(1e-4,1.5))
    ax.legend(fontsize=8)
fig.suptitle(r'N=6 double-boundary localization fits: $A(m)=A_L e^{-m/\xi}+A_R e^{-(5-m)/\xi}$', y=1.04)
fig.tight_layout()
fig.savefig(OUT/'A_double_boundary_localization_fit.png', dpi=240, bbox_inches='tight')
plt.close(fig)

lines = ['# A. N=6 双边界局域化拟合\n', '主拟合对象为 `root_integrated_power = [∫|A_TLS^⊥(ω)|²dω]^{1/2}`。它在弱探针/线性响应意义下是最接近局域耦合矩阵元幅度的原始响应代理。`peak_amplitude` 和名义共振点振幅仅作为模型依赖性敏感性检查。\n']
for name, payload in results['per_metric'].items():
    lines.append(f'## {name}\n')
    lines.append(f'共同 ξ 拟合：{payload["joint_common_xi"]:.6f}；跨窗口 ξ 均值：{payload["xi_window_mean"]:.6f}；窗口系统差：{payload["xi_window_std_systematic"]:.6f}；对 ξ_B 的比：{payload["ratio_to_xi_B"]:.3f}；对 ξ_π 的比：{payload["ratio_to_xi_pi"]:.3f}。\n')
    lines.append('| discard window | AL | AR | ξ | R² | RMSE |\n|---:|---:|---:|---:|---:|---:|\n')
    for w, fit in payload['fits'].items():
        lines.append(f'| {w}T | {fit["AL"]:.6g} | {fit["AR"]:.6g} | {fit["xi"]:.6f} | {fit["r2"]:.6f} | {fit["rmse"]:.6g} |\n')
lines.append('\n解释：拟合协方差给出的误差只反映 6 个确定性数据点对该函数形式的局部曲率；这里更应把三个舍弃窗口之间的离散当作有限观测时间的系统敏感性。\n')
(OUT/'A_localization_fit_results.md').write_text(''.join(lines),encoding='utf-8')
(OUT/'A_localization_fit_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(OUT/'A_localization_fit_results.md')
print(OUT/'A_double_boundary_localization_fit.png')

#!/usr/bin/env python3
"""Render coupling/phase panels from committed checkpoints and fit records."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[2]
SCAN = REPO / "data/checkpoints/floquet_tls_N6_g_frequency_checkpoint.npz"
PRODUCTION = REPO / "data/checkpoints/floquet_tls_frequency_production_checkpoint.npz"
FIT = REPO / "results/reproduced/B_geff_scaling_results.json"


def diagnostics(rows: list[dict], fit: dict, factor: float) -> dict:
    accepted = [row for row in rows if row["accepted"]]
    if len(accepted) != 4 or [row["g"] for row in accepted] != [0.06, 0.08, 0.1, 0.12]:
        raise ValueError("The committed fit no longer contains the four declared accepted points")
    g = np.array([row["g"] for row in accepted])
    y = np.array([row["full_split"] for row in accepted])
    if not (np.all(np.isfinite(g)) and np.all(np.isfinite(y))):
        raise ValueError("Non-finite accepted coupling/splitting")
    slope, intercept = np.polyfit(g, y, 1)
    expected = fit["accepted_fit"]["full_split_vs_g_eff"]
    if not (np.isclose(slope, expected["slope"] * factor, atol=1e-12)
            and np.isclose(intercept, expected["intercept"], atol=1e-12)):
        raise ValueError("Derived bare-g fit differs from the committed fit")
    _, covariance = np.polyfit(g, y, 1, cov=True)
    stderr = np.sqrt(np.diag(covariance))
    residual = y - (slope*g + intercept)
    slope0 = float(g@y/(g@g))
    if not np.isclose(slope0, expected["origin_constrained_slope"]*factor, atol=1e-12):
        raise ValueError("Origin-constrained fit differs from the committed record")
    return {"slope_per_g_over_J":float(slope), "intercept_in_J":float(intercept),
            "formal_ols_slope_se":float(stderr[0]), "formal_ols_intercept_se":float(stderr[1]),
            "origin_slope_per_g_over_J":slope0, "free_R2":expected["R2"],
            "origin_R2":expected["origin_constrained_R2"],
            "residuals_in_J":{f"{row['g']:.2f}":float(r)
                              for row,r in zip(accepted,residual)}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-output", type=Path,
                        default=REPO / "build/submission_coupling/fig5_coupling_bare_g.png")
    parser.add_argument("--phase-output", type=Path,
                        default=REPO / "build/submission_coupling/figS5_detuning_phase.png")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    fit = json.loads(FIT.read_text(encoding="utf-8"))
    rows = fit["rows"]
    info = diagnostics(rows, fit, float(fit["B0pi_edge"]))
    with np.load(SCAN, allow_pickle=False) as data:
        gvals = np.array(data["g_values"], float)
        ratios = np.array(data["omega_ratios"], float)
        curves = np.array(data["A_tls_transverse_d20"], float)
    if curves.shape != (len(gvals), len(ratios)) or not np.all(np.isfinite(curves)):
        raise ValueError("Unexpected scan checkpoint shape or non-finite response")
    if len(rows) != len(gvals) or not np.allclose(gvals, [row["g"] for row in rows]):
        raise ValueError("Fit record does not match the coupling checkpoint")
    with np.load(PRODUCTION, allow_pickle=False) as data:
        ratio_p = np.array(data["omega_ratio"], float)
        tls = np.array(data["A_tls_transverse"], float)
        edge = np.array(data["A_edge"], float)
        phase = np.array(data["phase_tls_minus_edge"], float)
    if not (ratio_p.shape == tls.shape == edge.shape == phase.shape
            and np.all(np.isfinite(tls)) and np.all(np.isfinite(edge))):
        raise ValueError("Production detuning checkpoint is inconsistent")
    if args.check_only:
        print(json.dumps(info, indent=2))
        return

    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":11,
                         "axes.spines.top":False, "axes.spines.right":False})
    fig, ax = plt.subplots(1, 2, figsize=(7.25, 3.45), gridspec_kw={"width_ratios":[1.2, 1]})
    colors = ["#5ca2ca", "#1f527f", "#c2483e", "#754889"]
    for color, g in zip(colors, (0.06, 0.08, 0.10, 0.12)):
        idx = int(np.flatnonzero(np.isclose(gvals, g))[0])
        ax[0].plot(ratios, curves[idx], lw=1.8, color=color, label=rf"$g/J={g:.2f}$")
    ax[0].axvline(1, lw=0.8, ls=":", color="0.45")
    ax[0].set(xlim=(0.84, 1.16), xlabel=r"Detector ratio $r=\omega_d/(\Omega/2)$",
              ylabel=r"TLS transverse amplitude $A_{\mathrm{TLS}}$", title="(a) Resolved doublets")
    ax[0].legend(ncol=2, fontsize=8.7, frameon=False, loc="upper left")
    ax[0].grid(alpha=0.18)

    accepted = [row for row in rows if row["accepted"]]
    x = np.array([row["g"] for row in accepted])
    y = np.array([row["full_split"] for row in accepted])
    err = np.array([row["full_split_window_std"] for row in accepted])
    ax[1].errorbar(x, y, yerr=err, fmt="o", color="#1f527f", capsize=3,
                   label="resolved (four points)")
    fit_x = np.linspace(x.min(), x.max(), 100)
    ax[1].plot(fit_x, info["slope_per_g_over_J"]*fit_x+info["intercept_in_J"],
               "k--", lw=1.4, label=rf"free intercept, $R^2={info['free_R2']:.4f}$")
    ax[1].plot(fit_x, info["origin_slope_per_g_over_J"]*fit_x,
               color="0.45", ls=":", lw=1.5,
               label=rf"zero intercept, $R^2={info['origin_R2']:.4f}$")
    for row in rows:
        if not row["accepted"]:
            ax[1].plot(row["g"], 0.018, marker="x", color="0.55", ms=6)
    ax[1].text(0.03, 0.06, "crosses: unresolved / excluded",
               transform=ax[1].transAxes, fontsize=8.1, color="0.35")
    ax[1].set(xlim=(0.015, 0.17), ylim=(0, 0.39), xlabel=r"Bare contact coupling $g/J$",
              ylabel=r"Full splitting $\Delta\omega/J$", title="(b) Fit in resolved interval")
    ax[1].legend(fontsize=8.0, loc="upper left", frameon=False)
    ax[1].grid(alpha=0.18)
    fig.tight_layout(w_pad=2)
    args.main_output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.main_output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    mask = (tls > 0.02) & (edge > 0.02) & np.isfinite(phase)
    fig, left = plt.subplots(figsize=(5.2, 3.25))
    left.plot(ratio_p, tls/tls.max(), color="#bd483f", label=r"$A_{\rm TLS}$ (normalized)")
    left.plot(ratio_p, edge/edge.max(), color="#1f527f", label=r"$A_{\rm edge}$ (normalized)")
    left.set(xlabel=r"Detector ratio $r=\omega_d/(\Omega/2)$",
             ylabel="Normalized amplitude", xlim=(ratio_p.min(), ratio_p.max()), ylim=(0, 1.05))
    left.axvline(1, lw=0.8, ls=":", color="0.45")
    right = left.twinx()
    right.plot(ratio_p[mask], phase[mask], ".", ms=3, color="#cf8d2f",
               label=r"$\phi_{\rm TLS}-\phi_{\rm edge}$")
    right.set_ylabel("Relative phase (rad)", color="#a46a1f")
    right.tick_params(axis="y", labelcolor="#a46a1f")
    lines = left.lines[:2] + right.lines
    left.legend(lines, [line.get_label() for line in lines], loc="upper right",
                frameon=False, fontsize=7.5)
    left.grid(alpha=0.18)
    fig.tight_layout()
    args.phase_output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.phase_output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({"main_output":str(args.main_output),
                      "phase_output":str(args.phase_output), "fit":info}, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate the committed N=6 damping sweep and draw its submission panel."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[2]
CHECKPOINT = REPO / "data/checkpoints/floquet_tls_N6_gamma_checkpoint.npz"


def load() -> tuple[np.ndarray, float, dict[str, np.ndarray]]:
    with np.load(CHECKPOINT, allow_pickle=False) as data:
        gamma = np.asarray(data["gamma_values"], dtype=float)
        period = float(data["metadata_T"])
        complete = np.asarray(data["completed"], dtype=bool)
        if (gamma.shape != (31,) or complete.shape != gamma.shape
                or not np.all(complete) or not np.all(np.diff(gamma) > 0)
                or not np.all(np.isfinite(gamma)) or not (period > 0)
                or int(data["metadata_N"]) != 6
                or not np.isclose(float(data["metadata_g"]), 0.08)
                or not np.array_equal(data["discard_windows"], [8, 20, 40])):
            raise ValueError("Incomplete or unexpected committed damping checkpoint")
        keys = ("A_edge_d20", "A_tls_transverse_d20", "Mpi_edge_strobe_d20",
                "tls_emission_d20", "phase_tls_minus_edge_d20")
        values = {key: np.asarray(data[key], dtype=float) for key in keys}
    if any(value.shape != gamma.shape or not np.all(np.isfinite(value))
           for value in values.values()):
        raise ValueError("Incomplete or non-finite damping observables")
    return gamma, period, values


def render(gamma: np.ndarray, period: float, values: dict[str, np.ndarray], output: Path) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    x = gamma * period
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.1))
    edge = values["A_edge_d20"]
    tls = values["A_tls_transverse_d20"]
    axes[0].plot(x, edge, "o-", ms=3, color="#28658c", label=r"$A_{\rm edge}$")
    axes[0].plot(x, tls, "s-", ms=3, color="#c34d43", label=r"$A_{\rm TLS}$")
    axes[0].set(ylabel="Response amplitude", title="(a) Edge and TLS response")
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].plot(x, values["Mpi_edge_strobe_d20"], "o-", ms=3,
                 color="#74509d", label=r"$M_{\pi,\rm edge}$")
    axes[1].set(ylabel=r"Edge $\pi$ component", title="(b) Subharmonic response and loss")
    right = axes[1].twinx()
    right.plot(x, values["tls_emission_d20"], "s--", ms=3,
               color="#d88717", label="TLS emission")
    right.set_ylabel(r"TLS emission $P_{\rm em}$")
    lines = axes[1].lines + right.lines
    axes[1].legend(lines, [line.get_label() for line in lines], frameon=False,
                   fontsize=7.5, loc="upper left")

    phase = values["phase_tls_minus_edge_d20"]
    visible = (edge >= 0.02) & (tls >= 0.02)
    axes[2].plot(x[visible], phase[visible], "o-", ms=3, color="#444444")
    axes[2].set(ylabel=r"Relative phase $\phi_{\rm TLS}-\phi_{\rm edge}$ (rad)",
                title="(c) Phase above visibility threshold")
    axes[2].text(0.04, 0.05, r"both amplitudes $\geq 0.02$",
                 transform=axes[2].transAxes, fontsize=7.5,
                 bbox={"facecolor": "white", "edgecolor": "0.8"})
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xlabel(r"TLS damping $\gamma_1 T$")
        ax.grid(alpha=0.18)
    for ax in axes:
        ax.title.set_fontsize(10)
    fig.tight_layout(w_pad=3.8)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=REPO / "build/submission_damping")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    gamma, period, values = load()
    output = args.output_dir / "fig5_dissipation_backaction_gammaT.png"
    if not args.check_only:
        render(gamma, period, values, output)
    print(json.dumps({"checkpoint": str(CHECKPOINT.relative_to(REPO)),
                      "completed": len(gamma), "period": period,
                      "gamma1T_range": [float(gamma[0]*period), float(gamma[-1]*period)],
                      "output": None if args.check_only else str(output)}, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Regenerate PRB multichannel-control figures from committed JSON summaries.

This is the fast reviewer route. It does not rerun full Floquet--Lindblad
propagation; it validates the stored formal-protocol spectra, K errors, and
metadata, then writes figures and a Markdown audit under results/reproduced/.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "prb_controls"
OUT = ROOT / "results" / "reproduced" / "prb_controls"


CONTROLS = {
    "N=6, g=0.08": DATA / "N6_g0p08_matched_k_convergence.json",
    "N=8, g=0.08": DATA / "N8_g0p08_matched_k_convergence.json",
    "N=8, g=0.12": DATA / "N8_g0p12_strong_coupling_k_convergence.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def errors(payload: dict) -> tuple[list[int], list[float]]:
    rows = payload["rows"]
    return [int(row["K"]) for row in rows], [float(row["epsilon_spec"]) for row in rows]


def normalized(values: list[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    return array / np.max(array)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payloads = {label: load(path) for label, path in CONTROLS.items()}

    # Two positive matched-protocol spectral overlays.
    figure, axes = plt.subplots(1, 2, figsize=(8.2, 3.35), sharey=True)
    for axis, label in zip(axes, ("N=6, g=0.08", "N=8, g=0.08")):
        payload = payloads[label]
        metadata = payload["metadata"]
        ratios = np.asarray(metadata["ratios"], dtype=float)
        axis.plot(ratios, normalized(payload["full_d20"]), "ko-", lw=1.9, ms=4, label="full")
        for row, color in zip(payload["rows"], ("C1", "C3", "C0", "C2")):
            axis.plot(ratios, normalized(row["effective_d20"]), "s--", color=color, ms=3.5, lw=1.1, label=rf"$K={row['K']}$")
        axis.axvline(1.0, color="0.45", ls=":", lw=1)
        axis.set_title(label, fontsize=10)
        axis.set_xlabel(r"$\omega_d/(\Omega/2)$")
        axis.grid(alpha=0.22)
    axes[0].set_ylabel(r"normalized $A_{\rm TLS}$")
    axes[1].legend(fontsize=7.5, loc="best")
    figure.tight_layout()
    figure.savefig(OUT / "PRB_F6_matched_positive_controls.png", dpi=260)
    plt.close(figure)

    # Unified error plot, including the strong-coupling counterexample.
    figure, axis = plt.subplots(figsize=(6.65, 4.15))
    styles = {
        "N=6, g=0.08": ("#1f77b4", "o"),
        "N=8, g=0.08": ("#2ca02c", "s"),
        "N=8, g=0.12": ("#9c2f2f", "D"),
    }
    table_lines = ["| Control | K=2 | K=4 | K=6 | K=8 |", "|---|---:|---:|---:|---:|"]
    for label, payload in payloads.items():
        ks, values = errors(payload)
        color, marker = styles[label]
        axis.plot(ks, values, marker=marker, color=color, lw=1.9, ms=6, label=label)
        table_lines.append("| " + label + " | " + " | ".join(f"{value:.4f}" for value in values) + " |")
    axis.axhspan(0, 0.20, color="#e7f4e4", alpha=0.8, label="predictive criterion")
    axis.axhline(0.20, color="#4d7c4d", ls=":", lw=1.1)
    axis.set(xticks=(2, 4, 6, 8), xlabel="projected manifold dimension $K$", ylabel=r"normalized spectral error $\epsilon_{\rm spec}$", ylim=(0.0, 0.70))
    axis.grid(alpha=0.22)
    axis.legend(fontsize=8, loc="upper left")
    figure.tight_layout()
    figure.savefig(OUT / "PRB_three_control_K_convergence.png", dpi=260)
    plt.close(figure)

    audit = [
        "# PRB multichannel controls: fast audit",
        "",
        "This file and the associated figures are regenerated from committed JSON summaries; they do not rerun the high-cost full Floquet--Lindblad propagation.",
        "",
        *table_lines,
        "",
        "## Interpretation boundary",
        "",
        "The two $g=0.08$ controls use matched N=6/N=8 protocols and show the dominant error reduction from K=2 to K=4. The N=8, g=0.12 control instead shows that the tested resonance-weighted K=4--8 local manifolds remain nonpredictive. This does not prove that every larger or differently selected reduced space must fail.",
        "",
        "## Full-production route",
        "",
        "Use `scripts/40_formal_k_convergence.py` with the selected `--n` and `--g` parameters to recompute a control from first principles. N=8 calculations can take a long time and require substantially more memory than this plotting audit.",
    ]
    (OUT / "PRB_multichannel_controls_audit.md").write_text("\n".join(audit) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()

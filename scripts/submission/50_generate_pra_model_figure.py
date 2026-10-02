"""Draw the platform-independent model and control schematic for the PRA draft."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "manuscript" / "figures" / "fig1_model_common_preparation_workflow"
BLUE = "#245A79"
ORANGE = "#A75712"
GREEN = "#267858"
INK = "#202934"


def panel(ax, tag, title):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.02, 0.96, tag, fontsize=15, fontweight="bold", va="top", color=INK)
    ax.text(0.11, 0.96, title, fontsize=13, fontweight="semibold", va="top", color=INK)


def box(ax, x, y, w, h, label, color=BLUE, size=12):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.014,rounding_size=0.024",
            linewidth=1.5, edgecolor=color, facecolor="white",
        )
    )
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=size, color=INK)


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans"})
    fig, axs = plt.subplots(2, 2, figsize=(13.2, 7.4))
    fig.subplots_adjust(left=0.04, right=0.98, top=0.97, bottom=0.06, wspace=0.09, hspace=0.22)
    a, b, c, d = axs.flat

    panel(a, "a", "Finite chain and local lossy probe")
    xs = [0.12 + 0.135 * j for j in range(6)]
    for j in range(5):
        a.plot([xs[j] + 0.045, xs[j + 1] - 0.045], [0.37, 0.37], color=BLUE, lw=2)
    for j, x in enumerate(xs):
        a.add_patch(Circle((x, 0.37), 0.045, facecolor="#DFEBF2", edgecolor=BLUE, lw=1.8))
        a.text(x, 0.37, str(j), ha="center", va="center", fontsize=11, color=INK)
    a.add_patch(Circle((xs[0], 0.72), 0.064, facecolor="#F7E8DB", edgecolor=ORANGE, lw=1.8))
    a.text(xs[0], 0.72, "TLS", ha="center", va="center", fontsize=11, color=INK)
    a.annotate("", (xs[0], 0.425), (xs[0], 0.65), arrowprops={"arrowstyle": "<->", "color": ORANGE, "lw": 1.8})
    a.text(0.27, 0.69, r"exchange $g$; TLS loss $\gamma_1$", fontsize=11.5, color=ORANGE)
    a.text(0.11, 0.13, r"TLS contact $x$ is movable", fontsize=11.5, color=INK)

    panel(b, "b", "Common physical preparation")
    box(b, 0.08, 0.50, 0.85, 0.23,
        r"$\rho(0)=|\uparrow_z\rangle\langle\uparrow_z|^{\otimes N}\otimes|0_d\rangle\langle0_d|$",
        color=GREEN, size=15)
    b.text(0.12, 0.29, "Same initial state for all principal comparisons", fontsize=12, color=INK)
    b.text(0.12, 0.17, "No Floquet-pair or topology-selected preparation", fontsize=11, color=INK)

    panel(c, "c", "Frequency-resolved TLS coherence")
    box(c, 0.08, 0.60, 0.82, 0.15, r"$c_d(t)=[\langle X_d\rangle+i\langle Y_d\rangle]/2$", size=14)
    c.annotate("", (0.49, 0.47), (0.49, 0.60), arrowprops={"arrowstyle": "->", "color": BLUE, "lw": 1.6})
    box(c, 0.08, 0.27, 0.82, 0.17, r"$A_{\rm TLS}(r)$  and  $W_{\rm r}=\int dr\,A_{\rm TLS}^{2}(r)$", color=ORANGE, size=14)
    c.text(0.13, 0.11, r"$r=\omega_d/(\Omega/2)$, with a declared detector grid", fontsize=11, color=INK)

    panel(d, "d", "Questions answered by the controls")
    box(d, 0.07, 0.68, 0.86, 0.13, "OBC/PBC and contact position: boundary selectivity", size=11.4)
    box(d, 0.07, 0.45, 0.86, 0.13, r"Matched drives: limits of the $\nu_\pi$ label", color=GREEN, size=11.4)
    box(d, 0.07, 0.22, 0.86, 0.13, r"Fixed eight-drive $N=4\rightarrow6$: weight transfer", color=ORANGE, size=11.2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.08)
    fig.savefig(OUT.with_suffix(".png"), dpi=220, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


if __name__ == "__main__":
    main()

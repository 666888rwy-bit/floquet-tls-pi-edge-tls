#!/usr/bin/env python3
"""Render the eight-drive N=4 to N=6 transfer from validated immutable records.

This submission figure imports the existing read-only Gate D2 audit and does not
propagate the model or alter the source result directory.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


REPO = Path(__file__).resolve().parents[2]
AUDIT_PATH = REPO / "scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py"


def load_audit():
    sys.path.insert(0, str(AUDIT_PATH.parent))
    spec = importlib.util.spec_from_file_location("gate_d2_read_only_audit", AUDIT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load the committed Gate D2 audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render(records: list[dict], decision: dict, path: Path) -> None:
    colors = {0: "#a96019", 1: "#256f9c"}
    markers = {"a": "o", "b": "s"}
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.65), sharey=True)
    for nu0, ax in enumerate(axes):
        subset = [row for row in records if row["nu0"] == nu0]
        for row in sorted(subset, key=lambda item: item["id"]):
            marker = markers[row["id"][-1]]
            color = colors[row["nupi"]]
            ax.plot([0, 1], [row["W_r_N4"], row["W_r_N6"]],
                    color=color, marker=marker, markersize=5.5,
                    linewidth=1.5, alpha=0.9)
            offset = {"nu01_a": 7, "nu01_b": -7}.get(row["id"], 0)
            ax.annotate(row["id"], (1, row["W_r_N6"]),
                        xytext=(5, offset), textcoords="offset points",
                        fontsize=8.4, va="center", color=color)
        ax.set(xlim=(-0.16, 1.42), ylim=(3e-8, 8e-2),
               yscale="log", xticks=[0, 1], xticklabels=["$N=4$", "$N=6$"],
               title=rf"Fixed $\nu_0={nu0}$")
        ax.grid(axis="y", which="both", alpha=0.18)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel(r"Raw integrated TLS weight $W_{\mathrm{r}}$")
    legend = [Line2D([0], [0], color=colors[k], marker="o", lw=1.5,
                     label=rf"$\nu_\pi={k}$") for k in (0, 1)]
    legend.extend([Line2D([0], [0], color="0.4", marker=markers[k],
                          linestyle="none", label=f"drive {k}") for k in ("a", "b")])
    fig.legend(handles=legend, loc="upper center", ncol=4,
               bbox_to_anchor=(0.5, 1.02), frameon=False, fontsize=9.5)
    fig.tight_layout(rect=(0, 0, 1, 0.91), w_pad=1.8)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=REPO / "build/submission_d2/fig4_d2_weight_transfer.png")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    audit, _ = load_audit().build_audit()
    records = audit["records"]
    decision = audit["frozen_confirmation"]
    if len(records) != 8 or len({row["id"] for row in records}) != 8:
        raise ValueError("The validated transfer must contain exactly eight distinct drives")
    if not args.check_only:
        render(records, decision, args.output)
    print(json.dumps({"figure": None if args.check_only else str(args.output),
                      "protocol_sha256": audit["protocol_sha256"],
                      "manifest_sha256": audit["manifest_sha256"],
                      "result_count": len(records), "decision": decision}, indent=2))


if __name__ == "__main__":
    main()

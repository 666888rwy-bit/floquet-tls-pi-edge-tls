#!/usr/bin/env python3
"""Generate manuscript-facing N=4 mechanism figures from committed benchmark data.

This script never recomputes the channel spectrum or refits the trace.  It validates
and re-renders the versioned ``C_N4_channel_time_validation_results.json`` artifact,
which keeps the inexpensive submission-figure path separate from the scientific
production calculation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "results/reproduced/C_N4_channel_time_validation_results.json"
DEFAULT_OUTPUT = REPO / "build/submission_mechanisms"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "mathtext.fontset": "dejavusans",
        "axes.unicode_minus": False,
        "font.size": 10,
        "axes.grid": True,
        "grid.alpha": 0.25,
    }
)


class BenchmarkValidationError(ValueError):
    """Raised when the committed N=4 benchmark lacks required, finite quantities."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_scalar(mapping: dict[str, Any], field: str) -> float:
    value = mapping.get(field)
    if not isinstance(value, (int, float)) or not np.isfinite(value):
        raise BenchmarkValidationError(f"{field} must be a finite scalar")
    return float(value)


def finite_vector(mapping: dict[str, Any], field: str) -> np.ndarray:
    value = np.asarray(mapping.get(field), dtype=float)
    if value.ndim != 1 or value.size < 3 or not np.all(np.isfinite(value)):
        raise BenchmarkValidationError(f"{field} must be a finite one-dimensional vector")
    return value


def validate_benchmark(record: dict[str, Any]) -> dict[str, float]:
    parameters = record.get("parameters")
    channel = record.get("channel")
    fit = record.get("time_fit_primary")
    if not isinstance(parameters, dict) or not isinstance(channel, dict) or not isinstance(fit, dict):
        raise BenchmarkValidationError("Benchmark record is missing parameters, channel, or time_fit_primary")
    if int(parameters.get("N", -1)) != 4:
        raise BenchmarkValidationError("Mechanism figure is defined only for the committed N=4 benchmark")
    n = finite_vector(fit, "n")
    data = finite_vector(fit, "data")
    curve = finite_vector(fit, "fit")
    if not (n.shape == data.shape == curve.shape) or not np.all(np.diff(n) > 0.0):
        raise BenchmarkValidationError("Primary fit trace arrays must share a strictly increasing period grid")
    if not bool(fit.get("success")):
        raise BenchmarkValidationError("Committed primary time-domain fit is not marked successful")
    tau_channel = finite_scalar(channel, "tau_periods")
    delta_channel = finite_scalar(channel, "delta_per_period")
    tau_fit = finite_scalar(fit, "tau_periods")
    delta_fit = finite_scalar(fit, "delta_per_period")
    conjugacy_error = finite_scalar(channel, "pair_conjugacy_error")
    if tau_channel <= 0.0 or tau_fit <= 0.0 or delta_channel <= 0.0 or delta_fit <= 0.0:
        raise BenchmarkValidationError("Channel and fit decay/offset values must be positive")
    return {
        "tau_channel_periods": tau_channel,
        "delta_channel_per_period": delta_channel,
        "tau_fit_periods": tau_fit,
        "delta_fit_per_period": delta_fit,
        "pair_conjugacy_error": conjugacy_error,
        "primary_fit_rmse": finite_scalar(fit, "rmse"),
        "primary_window_start": float(n[0]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE, help="Committed N=4 benchmark JSON")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Directory for derived manuscript figure files")
    parser.add_argument("--check-only", action="store_true", help="Validate the source artifact without writing figures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    record = json.loads(source.read_text(encoding="utf-8"))
    diagnostics = validate_benchmark(record)
    summary = {
        "schema": "floquet_tls_n4_mechanism_figure_v1",
        "source": str(source.relative_to(REPO)),
        "source_sha256": sha256(source),
        "diagnostics": diagnostics,
        "interpretation_boundary": "This is an exact N=4 channel/time benchmark for a prepared mechanism diagnostic. It is not a general common-preparation reduced theory for the N=6 full-model response.",
    }
    print(json.dumps(summary, indent=2))
    if args.check_only:
        return

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    fit = record["time_fit_primary"]
    n = finite_vector(fit, "n")
    data = finite_vector(fit, "data")
    curve = finite_vector(fit, "fit")

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.1), constrained_layout=True)
    axes[0].plot(n, data, "o", ms=3.0, color="0.32", label=r"raw $\langle Z_0\rangle$")
    axes[0].plot(n, curve, "-", lw=2.0, color="#c44e52", label="independent damped-cosine fit")
    axes[0].axvline(n[0], color="0.45", lw=1.0, ls=":", label=fr"primary window $n\geq {int(n[0])}$")
    axes[0].set(xlabel="Floquet period $n$", ylabel=r"edge magnetization $\langle Z_0\rangle$", title="N=4 stroboscopic trace")
    axes[0].legend(fontsize=8, frameon=True)

    labels = ["channel", "time fit"]
    positions = np.arange(2)
    width = 0.34
    axes[1].bar(positions - width / 2, [diagnostics["tau_channel_periods"], diagnostics["tau_fit_periods"]], width, color="#4c72b0", label=r"$\tau/T$")
    axes[1].set(xticks=positions, xticklabels=labels, ylabel=r"decay time $\tau/T$", title="Channel--time benchmark")
    phase_axis = axes[1].twinx()
    phase_axis.bar(positions + width / 2, [diagnostics["delta_channel_per_period"], diagnostics["delta_fit_per_period"]], width, color="#dd8452", label=r"$|\delta|$ [rad/period]")
    phase_axis.set_ylabel(r"phase offset $|\delta|$ [rad/period]")
    handles_left, labels_left = axes[1].get_legend_handles_labels()
    handles_right, labels_right = phase_axis.get_legend_handles_labels()
    axes[1].legend(handles_left + handles_right, labels_left + labels_right, loc="upper left", fontsize=8, frameon=True)
    fig.savefig(output / "FIG5_N4_CHANNEL_TIME_BENCHMARK.png", dpi=300)
    fig.savefig(output / "FIG5_N4_CHANNEL_TIME_BENCHMARK.pdf")
    plt.close(fig)
    (output / "FIG5_N4_CHANNEL_TIME_BENCHMARK.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

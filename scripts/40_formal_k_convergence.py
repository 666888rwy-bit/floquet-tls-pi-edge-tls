#!/usr/bin/env python3
"""Formal Floquet--TLS K-convergence control.

This direct-production script reproduces the matched protocol used for the
published N=6/N=8 multichannel controls. It is intentionally expensive for
N=8 because each detuning requires full sparse Floquet--Lindblad propagation.
Use the committed JSON files for a fast audit; run this script to independently
recompute a specified control.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm, schur
from scipy.sparse import csr_matrix, eye, kron
from scipy.sparse.linalg import expm_multiply

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, choices=(6, 8), required=True, help="Chain length.")
    parser.add_argument("--g", type=float, required=True, help="Local exchange coupling.")
    parser.add_argument("--gamma1", type=float, default=0.08, help="TLS amplitude-damping rate.")
    parser.add_argument("--periods", type=int, default=80, help="Total drive periods.")
    parser.add_argument("--samples-per-half", type=int, default=4, help="Continuous samples per drive half-step.")
    parser.add_argument("--discard-periods", type=int, default=20, help="Transient periods removed before phasor extraction.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory; default is results/reproduced/prb_controls/<tag>.")
    return parser.parse_args()


def tag_for(n: int, g: float, gamma1: float) -> str:
    return f"N{n}_g{g:.2f}_gamma{gamma1:.2f}".replace(".", "p")


def run(args: argparse.Namespace) -> Path:
    out = args.output_dir or ROOT / "results" / "reproduced" / "prb_controls" / tag_for(args.n, args.g, args.gamma1)
    out.mkdir(parents=True, exist_ok=True)

    n = args.n
    j = h = 1.0
    alpha = 0.75 * np.pi
    beta = 0.90 * np.pi
    t1 = beta / (2 * j)
    t2 = alpha / (2 * h)
    period = t1 + t2
    omega = 2 * np.pi / period
    half_omega = omega / 2
    ratios = np.linspace(0.88, 1.12, 11)
    subspace_sizes = (2, 4, 6, 8)

    i2_dense = np.eye(2, dtype=complex)
    x2_dense = np.array([[0, 1], [1, 0]], dtype=complex)
    z2_dense = np.diag([1.0, -1.0]).astype(complex)
    sm2_dense = np.array([[0, 1], [0, 0]], dtype=complex)
    i2 = csr_matrix(i2_dense)
    x2 = csr_matrix(x2_dense)
    z2 = csr_matrix(z2_dense)
    sm2 = csr_matrix(sm2_dense)

    def dense_kron(factors: list[np.ndarray]) -> np.ndarray:
        answer = np.array([[1.0 + 0.0j]])
        for factor in factors:
            answer = np.kron(answer, factor)
        return answer

    def sparse_kron(factors: list[csr_matrix]) -> csr_matrix:
        answer = csr_matrix([[1.0 + 0.0j]])
        for factor in factors:
            answer = kron(answer, factor, format="csr")
        return answer

    def dense_operator(operator: np.ndarray, site: int) -> np.ndarray:
        return dense_kron([operator if index == site else i2_dense for index in range(n)])

    def sparse_operator(operator: csr_matrix, site: int, total_sites: int) -> csr_matrix:
        return sparse_kron([operator if index == site else i2 for index in range(total_sites)])

    def spectral_propagator(eigenvalues: np.ndarray, eigenvectors: np.ndarray, time: float) -> np.ndarray:
        return (eigenvectors * np.exp(-1j * eigenvalues * time)) @ eigenvectors.conj().T

    def liouvillian(hamiltonian: csr_matrix, collapse: csr_matrix) -> csr_matrix:
        dimension = hamiltonian.shape[0]
        identity = eye(dimension, format="csr", dtype=complex)
        cdagc = collapse.getH() @ collapse
        return (
            -1j * (kron(identity, hamiltonian, format="csr") - kron(hamiltonian.T, identity, format="csr"))
            + kron(collapse.conjugate(), collapse, format="csr")
            - 0.5 * kron(identity, cdagc, format="csr")
            - 0.5 * kron(cdagc.T, identity, format="csr")
        ).tocsr()

    def expectation(operator: csr_matrix, vectorized_density: np.ndarray, dimension: int) -> complex:
        density = vectorized_density.reshape((dimension, dimension), order="F")
        return np.trace(operator.toarray() @ density)

    def subharmonic_phasor(times: np.ndarray, values: np.ndarray) -> float:
        mask = times >= args.discard_periods * period
        selected_times = times[mask]
        selected_values = np.asarray(values)[mask]
        selected_values = selected_values - selected_values.mean()
        return float(abs(2 * np.trapezoid(selected_values * np.exp(1j * half_omega * selected_times), selected_times) / (selected_times[-1] - selected_times[0])))

    # Closed Floquet basis and time-averaged local exchange matrix element.
    x_closed = [dense_operator(x2_dense, site) for site in range(n)]
    z_closed = [dense_operator(z2_dense, site) for site in range(n)]
    sm_closed = dense_operator(sm2_dense, 0)
    h1_closed = sum((-j * z_closed[site] @ z_closed[site + 1] for site in range(n - 1)), start=np.zeros((2**n, 2**n), dtype=complex))
    h2_closed = sum((-h * operator for operator in x_closed), start=np.zeros((2**n, 2**n), dtype=complex))
    eig1, vec1 = np.linalg.eigh(h1_closed)
    eig2, vec2 = np.linalg.eigh(h2_closed)
    u1 = spectral_propagator(eig1, vec1, t1)
    u2 = spectral_propagator(eig2, vec2, t2)
    triangular, floquet_vectors = schur(u2 @ u1, output="complex")
    phases = np.angle(np.diag(triangular))
    quasienergies = -phases / period

    local_matrix = np.zeros((2**n, 2**n), dtype=complex)
    time_grid = np.linspace(0, period, 241)
    for index, time in enumerate(time_grid):
        evolution = spectral_propagator(eig1, vec1, time) if time <= t1 + 1e-14 else spectral_propagator(eig2, vec2, time - t1) @ u1
        micromotion = evolution @ floquet_vectors * np.exp(1j * quasienergies * time)[None, :]
        local_matrix += (0.5 if index in (0, len(time_grid) - 1) else 1.0) * (micromotion.conj().T @ sm_closed @ micromotion)
    local_matrix *= (time_grid[1] - time_grid[0]) / period

    candidate_pairs = []
    for first in range(2**n):
        for second in range(first + 1, 2**n):
            mismatch = abs(np.angle(np.exp(1j * (phases[second] - phases[first] - np.pi))))
            if mismatch <= 0.02:
                amplitude = max(abs(local_matrix[first, second]), abs(local_matrix[second, first]))
                candidate_pairs.append((amplitude, mismatch, first, second))
    target_amplitude, target_mismatch, first, second = max(candidate_pairs, key=lambda row: row[0])
    target_pair = [first, second]

    ranked_channels = []
    for channel in range(2**n):
        if channel in target_pair:
            continue
        local_weight = float(sum(abs(local_matrix[channel, pair_index]) ** 2 + abs(local_matrix[pair_index, channel]) ** 2 for pair_index in target_pair))
        detuning = min(abs(np.angle(np.exp(1j * (phases[channel] - phases[pair_index])))) / period for pair_index in target_pair)
        ranked_channels.append((local_weight / (detuning**2 + (0.05 * omega) ** 2), channel, local_weight, detuning))
    ranked_channels.sort(reverse=True)
    external_channels = [channel for _, channel, _, _ in ranked_channels]
    subspaces = {k: target_pair + external_channels[: k - 2] for k in subspace_sizes}

    z_matrix_element = floquet_vectors[:, first].conj() @ z_closed[0] @ floquet_vectors[:, second]
    pair_coefficients = np.array([1.0, np.exp(-1j * np.angle(z_matrix_element))], dtype=complex) / np.sqrt(2)

    # Full open Floquet--Lindblad propagation.
    total_sites = n + 1
    full_dimension = 2**total_sites
    z_full = [sparse_operator(z2, site, total_sites) for site in range(total_sites)]
    x_full = [sparse_operator(x2, site, total_sites) for site in range(total_sites)]
    sm_full = [sparse_operator(sm2, site, total_sites) for site in range(total_sites)]
    hzz = sum((-j * (z_full[site] @ z_full[site + 1]) for site in range(n - 1)), start=csr_matrix((full_dimension, full_dimension), dtype=complex))
    hx = sum((-h * operator for operator in x_full[:n]), start=csr_matrix((full_dimension, full_dimension), dtype=complex))
    h_tls = -0.5 * z_full[n]
    h_interaction = sm_full[0].getH() @ sm_full[n] + sm_full[0] @ sm_full[n].getH()
    tls_lowering = sm_full[n]
    collapse = np.sqrt(args.gamma1) * sm_full[n]
    initial_state = np.kron(floquet_vectors[:, target_pair] @ pair_coefficients, np.array([1.0, 0.0], dtype=complex))
    full_density = np.outer(initial_state, initial_state.conj()).reshape(-1, order="F")

    def full_response(ratio: float) -> float:
        l1 = liouvillian(hzz + ratio * half_omega * h_tls + args.g * h_interaction, collapse)
        l2 = liouvillian(hx + ratio * half_omega * h_tls + args.g * h_interaction, collapse)
        vector = full_density.copy()
        times: list[float] = []
        values: list[complex] = []
        current_time = 0.0
        for _ in range(args.periods):
            first_step = expm_multiply(l1, vector, start=0, stop=t1, num=args.samples_per_half + 1, endpoint=True)
            for sample in range(args.samples_per_half):
                times.append(current_time + sample * t1 / args.samples_per_half)
                values.append(expectation(tls_lowering, first_step[sample], full_dimension))
            vector = first_step[-1]
            current_time += t1
            second_step = expm_multiply(l2, vector, start=0, stop=t2, num=args.samples_per_half + 1, endpoint=True)
            for sample in range(args.samples_per_half):
                times.append(current_time + sample * t2 / args.samples_per_half)
                values.append(expectation(tls_lowering, second_step[sample], full_dimension))
            vector = second_step[-1]
            current_time += t2
        return subharmonic_phasor(np.asarray(times), np.asarray(values))

    def projected_response(ratio: float, indices: list[int]) -> float:
        k = len(indices)
        effective_energies = quasienergies[indices] - np.mean(quasienergies[indices])
        b_projected = local_matrix[np.ix_(indices, indices)]
        dimension = 2 * k
        observable = np.kron(np.eye(k), sm2_dense)
        projected_collapse = np.sqrt(args.gamma1) * observable
        cdagc = projected_collapse.conj().T @ projected_collapse
        hamiltonian = (
            np.kron(np.diag(effective_energies), i2_dense)
            + np.kron(np.eye(k), -0.5 * ratio * half_omega * z2_dense)
            + args.g * (np.kron(b_projected.conj().T, sm2_dense) + np.kron(b_projected, sm2_dense.conj().T))
        )
        identity = np.eye(dimension, dtype=complex)
        generator = (
            -1j * (np.kron(identity, hamiltonian) - np.kron(hamiltonian.T, identity))
            + np.kron(projected_collapse.conj(), projected_collapse)
            - 0.5 * np.kron(identity, cdagc)
            - 0.5 * np.kron(cdagc.T, identity)
        )
        step1 = expm(generator * (t1 / args.samples_per_half))
        step2 = expm(generator * (t2 / args.samples_per_half))
        state = np.zeros(2 * k, dtype=complex)
        state[0] = pair_coefficients[0]
        state[2] = pair_coefficients[1]
        vector = np.outer(state, state.conj()).reshape(-1, order="F")
        times: list[float] = []
        values: list[complex] = []
        current_time = 0.0
        for _ in range(args.periods):
            for _ in range(args.samples_per_half):
                times.append(current_time)
                values.append(np.trace(observable @ vector.reshape((dimension, dimension), order="F")))
                vector = step1 @ vector
                current_time += t1 / args.samples_per_half
            for _ in range(args.samples_per_half):
                times.append(current_time)
                values.append(np.trace(observable @ vector.reshape((dimension, dimension), order="F")))
                vector = step2 @ vector
                current_time += t2 / args.samples_per_half
        return subharmonic_phasor(np.asarray(times), np.asarray(values))

    full_spectrum = []
    for ratio in ratios:
        full_spectrum.append(full_response(float(ratio)))
        print(f"full ratio={ratio:.3f}", flush=True)
    full_spectrum = np.asarray(full_spectrum)

    rows = []
    for k, indices in subspaces.items():
        spectrum = np.asarray([projected_response(float(ratio), indices) for ratio in ratios])
        error = float(np.linalg.norm(full_spectrum / max(np.linalg.norm(full_spectrum), 1e-15) - spectrum / max(np.linalg.norm(spectrum), 1e-15)))
        rows.append({"K": k, "indices": [int(index) for index in indices], "effective_d20": spectrum.tolist(), "epsilon_spec": error})
        print(f"K={k} epsilon_spec={error:.4f}", flush=True)

    payload = {
        "metadata": {
            "N": n,
            "g": args.g,
            "gamma1": args.gamma1,
            "ratios": ratios.tolist(),
            "periods": args.periods,
            "samples_per_half": args.samples_per_half,
            "discard_periods": args.discard_periods,
            "readout": "continuous-time phasor at Omega/2",
        },
        "projection": {
            "target_pair": target_pair,
            "target_B0pi": float(target_amplitude),
            "target_pi_mismatch": float(target_mismatch),
            "resonance_ranked_external": [int(index) for index in external_channels[:10]],
            "weight_rule": "top resonance-weighted external local spectral channels",
        },
        "full_d20": full_spectrum.tolist(),
        "rows": rows,
    }
    json_path = out / "formal_k_convergence.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    figure, axis = plt.subplots(figsize=(7.8, 4.6))
    axis.plot(ratios, full_spectrum / full_spectrum.max(), "ko-", label=f"full N={n}", lw=2, ms=4)
    for row, color in zip(rows, ("C1", "C3", "C0", "C2")):
        spectrum = np.asarray(row["effective_d20"])
        axis.plot(ratios, spectrum / max(spectrum.max(), 1e-15), marker="s", ls="--", color=color, label=rf"K={row['K']}, $\epsilon={row['epsilon_spec']:.2f}$")
    axis.axvline(1.0, color="0.4", ls=":")
    axis.set(xlabel=r"$\omega_d/(\Omega/2)$", ylabel=r"normalized $A_{\rm TLS}$", title=rf"N={n}, $g={args.g:.2f}$ formal Floquet truncation convergence")
    axis.grid(alpha=0.25)
    axis.legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(out / "formal_k_convergence.png", dpi=240)
    plt.close(figure)
    return json_path


if __name__ == "__main__":
    output = run(parse_args())
    print(output)

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm
from scipy.sparse.linalg import expm_multiply

REPO = Path(__file__).resolve().parents[1]
CORE_PATH = REPO / "scripts/gate_a_v2/10_full_model_common_preparation.py"
SPEC = importlib.util.spec_from_file_location("floquet_tls_full_model_core", CORE_PATH)
assert SPEC is not None and SPEC.loader is not None
CORE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CORE
SPEC.loader.exec_module(CORE)

build_system = CORE.build_system
liouvillian = CORE.liouvillian
make_timing = CORE.make_timing
tls_phasor = CORE.tls_phasor
response_at_ratio = CORE.response_at_ratio


def test_system_operators_are_hermitian_and_have_expected_dimension() -> None:
    system = build_system(n_chain=2, jcoupling=1.0, hfield=1.0, boundary="OBC", contact=0, gamma1=0.1)
    assert system.dim == 8
    for operator in (system.hzz, system.hx, system.hd, system.hint):
        assert np.linalg.norm((operator - operator.getH()).toarray()) < 1e-13


def test_pbc_adds_one_ising_link_relative_to_obc() -> None:
    obc = build_system(n_chain=3, jcoupling=1.0, hfield=1.0, boundary="OBC", contact=0, gamma1=0.0)
    pbc = build_system(n_chain=3, jcoupling=1.0, hfield=1.0, boundary="PBC", contact=0, gamma1=0.0)
    assert np.linalg.norm((pbc.hzz - obc.hzz).toarray()) > 1e-10


def test_liouvillian_is_trace_preserving() -> None:
    system = build_system(n_chain=2, jcoupling=1.0, hfield=1.0, boundary="OBC", contact=1, gamma1=0.17)
    generator = liouvillian(system.hzz + 0.3 * system.hx + 0.11 * system.hint, system.collapse)
    trace_row = np.eye(system.dim, dtype=complex).reshape(-1, order="F").conj()
    assert np.linalg.norm(trace_row @ generator.toarray()) < 1e-12


def test_zero_damping_liouvillian_matches_direct_unitary_evolution() -> None:
    system = build_system(n_chain=2, jcoupling=1.0, hfield=1.0, boundary="OBC", contact=0, gamma1=0.0)
    hamiltonian = system.hzz + 0.37 * system.hx + 0.13 * system.hint + 0.05 * system.hd
    time = 0.19
    propagated_vector = expm_multiply(liouvillian(hamiltonian, system.collapse) * time, system.rho_initial)
    propagated_density = propagated_vector.reshape((system.dim, system.dim), order="F")
    unitary = expm(-1j * hamiltonian.toarray() * time)
    direct_density = unitary @ system.rho_initial.reshape((system.dim, system.dim), order="F") @ unitary.conj().T
    assert np.allclose(propagated_density, direct_density, rtol=1e-11, atol=1e-12)
    assert np.trace(propagated_density) == pytest.approx(1.0 + 0.0j, abs=1e-12)


def test_decoupled_tls_has_no_transverse_phasor_from_the_declared_ground_state() -> None:
    system = build_system(n_chain=2, jcoupling=1.0, hfield=1.0, boundary="OBC", contact=0, gamma1=0.08)
    timing = make_timing(alpha_over_pi=0.75, beta_over_pi=0.90, jcoupling=1.0, hfield=1.0)
    response = response_at_ratio(
        system,
        timing,
        ratio=1.0,
        g=0.0,
        periods=4,
        samples_per_half=3,
        discard_periods=1,
    )
    assert response < 1e-12


def test_tls_phasor_removes_constant_offset_and_recovers_known_subharmonic_signal() -> None:
    omega = 2.3
    amplitude = 0.17
    times = np.linspace(0.0, 8.0 * np.pi / omega, 4097)
    values = amplitude * np.exp(-1j * omega * times / 2.0) + (0.3 - 0.2j)
    observed = tls_phasor(times, values, discard_time=0.0, omega=omega)
    assert observed == pytest.approx(2.0 * amplitude, rel=2e-4)
    constant_values = np.full(times.shape, 0.7 + 0.1j, dtype=complex)
    assert tls_phasor(times, constant_values, discard_time=0.0, omega=omega) < 1e-13

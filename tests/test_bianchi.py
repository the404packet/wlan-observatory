"""Unit and integration tests for Bianchi DCF analytical model."""
import pytest
from src.simulation.bianchi import solve_bianchi_tau, compute_bianchi_throughput


def test_bianchi_single_station():
    p, tau = solve_bianchi_tau(n_stations=1, cw_min=15, cw_max=1023)
    assert p == 0.0
    assert tau > 0.0


def test_bianchi_collision_monotonicity():
    """As station count increases, collision probability p must monotonically increase."""
    p_prev = 0.0
    for n in [2, 5, 10, 20, 30]:
        p, tau = solve_bianchi_tau(n_stations=n, cw_min=15, cw_max=1023)
        assert p > p_prev
        assert 0.0 < p < 1.0
        p_prev = p


def test_bianchi_throughput_physical_bounds():
    """Throughput must be positive and not exceed channel data rate."""
    res = compute_bianchi_throughput(n_stations=5, data_rate_mbps=6.0)
    assert 0.0 < res["throughput_mbps"] < 6.0
    assert 0.0 < res["normalized_throughput"] < 1.0

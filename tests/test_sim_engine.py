"""Unit and behavioral tests for CSMA/CA discrete-event simulation engine."""
import pytest
from src.simulation.engine import CsmaSimulator


def test_single_station_zero_collisions():
    """A single saturated station will never experience collisions."""
    sim = CsmaSimulator(n_stations=1, frame_error_prob=0.0, seed=123)
    res = sim.run(max_events=300)
    assert res["metrics"]["collision_probability"] == 0.0
    assert res["metrics"]["aggregate_throughput_mbps"] > 0.0


def test_multi_station_fairness_and_collisions():
    """Multi-station contending medium produces collisions and finite fairness index."""
    sim = CsmaSimulator(n_stations=5, frame_error_prob=0.0, seed=456)
    res = sim.run(max_events=500)
    assert res["metrics"]["collision_probability"] > 0.0
    assert 0.0 < res["metrics"]["jains_fairness_index"] <= 1.0
    assert len(res["timeline"]) > 0


def test_timeline_integrity():
    """Verify timeline events contain proper station counters and event types."""
    sim = CsmaSimulator(n_stations=3, seed=789)
    res = sim.run(max_events=50)
    for evt in res["timeline"]:
        assert "start_time_us" in evt
        assert "duration_us" in evt
        assert evt["type"] in ["IDLE", "SUCCESS", "COLLISION", "DROP"]
        assert isinstance(evt["counters"], dict)

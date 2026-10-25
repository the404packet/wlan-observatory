"""Unit tests for DCF backoff stages and contention window."""
import random
import pytest
from src.simulation.backoff import BackoffState, BackoffStrategy


def test_beb_doubling():
    rng = random.Random(42)
    b = BackoffState(cw_min=15, cw_max=1023, strategy=BackoffStrategy.BEB)
    assert b.current_cw == 15
    assert b.stage == 0

    retained = b.double_cw_on_failure(rng)
    assert retained is True
    assert b.stage == 1
    assert b.current_cw == 31

    b.double_cw_on_failure(rng)
    assert b.stage == 2
    assert b.current_cw == 63


def test_fixed_window_stays_constant():
    rng = random.Random(42)
    b = BackoffState(cw_min=31, cw_max=1023, strategy=BackoffStrategy.FIXED)
    assert b.current_cw == 31

    b.double_cw_on_failure(rng)
    assert b.current_cw == 31


def test_retry_limit_drop():
    rng = random.Random(42)
    b = BackoffState(cw_min=15, retry_limit=2)
    assert b.double_cw_on_failure(rng) is True  # retry 1
    assert b.double_cw_on_failure(rng) is True  # retry 2
    assert b.double_cw_on_failure(rng) is False  # retry 3 > retry_limit -> drop
    assert b.current_cw == 15

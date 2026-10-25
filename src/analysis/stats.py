"""Statistical utility functions and metric calculations."""
from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

import numpy as np
from scipy import stats


def mean_confidence_interval(
    data: Iterable[float], confidence: float = 0.95
) -> Tuple[float, float, float]:
    """Calculate mean and (lower, upper) confidence interval bounds using Student-t distribution."""
    arr = np.array(list(data), dtype=np.float64)
    arr = arr[~np.isnan(arr)]
    n = len(arr)
    if n < 2:
        val = float(arr[0]) if n == 1 else 0.0
        return val, val, val

    mean = float(np.mean(arr))
    sem = float(stats.sem(arr))
    h = sem * stats.t.ppf((1 + confidence) / 2.0, n - 1)
    return mean, mean - h, mean + h


def jains_fairness_index(values: Iterable[float]) -> float:
    """Compute Jain's Fairness Index for resource allocation or throughput across nodes.

    J(x) = (sum(x_i))^2 / (n * sum(x_i^2))
    Range is [1/n, 1.0], where 1.0 is perfectly fair.
    """
    arr = np.array(list(values), dtype=np.float64)
    if len(arr) == 0:
        return 1.0
    sum_vals = float(np.sum(arr))
    sum_sq = float(np.sum(arr**2))
    if sum_sq == 0:
        return 1.0
    return float((sum_vals**2) / (len(arr) * sum_sq))

"""Confidence intervals, rank stability, and sensitivity analysis."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.analysis.stats import mean_confidence_interval
from src.pipeline.ranking import DEFAULT_ANCHORS, DEFAULT_WEIGHTS, rank_channels_for_link


def compute_channel_confidence(
    df_raw_samples: pd.DataFrame, confidence: float = 0.95
) -> Dict[str, Dict[str, float]]:
    """Compute Student-t confidence intervals for SNR, RSS, and Noise."""
    res = {}
    for col in ["snr", "rss", "noise"]:
        if col in df_raw_samples.columns:
            m, low, high = mean_confidence_interval(df_raw_samples[col], confidence=confidence)
            res[col] = {"mean": round(m, 2), "ci_lower": round(low, 2), "ci_upper": round(high, 2)}
    return res


def run_sensitivity_analysis(
    df_summaries: pd.DataFrame,
    section: str,
    link_id: int,
    weight_key: str = "w_snr",
    values: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Evaluate how channel rank ordering shifts as a given weight sweeps across values."""
    if values is None:
        values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    # Baseline weights
    base_weights = dict(DEFAULT_WEIGHTS)
    other_keys = [k for k in base_weights if k != weight_key]

    results = []
    for val in values:
        w = dict(base_weights)
        w[weight_key] = val
        # Normalize the other weights so total sums to 1.0
        rem = max(0.0, 1.0 - val)
        base_rem = sum(base_weights[k] for k in other_keys)
        for k in other_keys:
            w[k] = (base_weights[k] / base_rem) * rem if base_rem > 0 else 0.0

        ranked = rank_channels_for_link(df_summaries, section, link_id, weights=w)
        ranks = {r["channel"]: r["rank"] for r in ranked}
        results.append({
            "param_value": val,
            "weights": {k: round(v, 3) for k, v in w.items()},
            "ranks": ranks,
        })

    return {
        "varied_weight": weight_key,
        "sweeps": results,
    }

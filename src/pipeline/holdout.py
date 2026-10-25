"""Temporal hold-out evaluation and ranking regret computation."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from config import settings
from src.analysis.metrics import calculate_rank_score
from src.pipeline.ranking import DEFAULT_ANCHORS, DEFAULT_WEIGHTS


def evaluate_temporal_holdout(
    df_raw: pd.DataFrame,
    split_ratio: float = 0.5,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Train channel ranking on first half of trace timeline, evaluate ranking regret on second half."""
    if weights is None:
        weights = DEFAULT_WEIGHTS

    n = len(df_raw)
    if n < 20:
        return {"status": "INSUFFICIENT_DATA", "records": n}

    # Sort strictly by timestamp
    df_sorted = df_raw.sort_values(by="timestamp").reset_index(drop=True)
    split_idx = int(n * split_ratio)

    train_df = df_sorted.iloc[:split_idx]
    test_df = df_sorted.iloc[split_idx:]

    def score_split(d: pd.DataFrame) -> float:
        snr_m = float(d["snr"].mean())
        snr_s = float(d["snr"].std(ddof=1)) if len(d) > 1 else 0.0
        stab = 1.0 / (1.0 + snr_s)
        noise_m = float(d["noise"].mean())
        rate_m = float(d["data_rate"].mode().iloc[0]) if len(d["data_rate"].mode()) > 0 else 6.0
        return calculate_rank_score(snr_m, stab, noise_m, rate_m, weights, DEFAULT_ANCHORS)["score"]

    train_score = score_split(train_df)
    test_score = score_split(test_df)
    drift = test_score - train_score

    return {
        "status": "EVALUATED",
        "train_records": len(train_df),
        "test_records": len(test_df),
        "train_score": round(train_score, 2),
        "test_score": round(test_score, 2),
        "score_drift": round(drift, 2),
        "stability_ratio": round(min(train_score, test_score) / (max(train_score, test_score) + 1e-6), 3),
    }

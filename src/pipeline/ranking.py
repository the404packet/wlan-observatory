"""Explainable channel ranking engine for wireless trace measurements."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.analysis.metrics import calculate_rank_score

# Fixed, documented score anchors across 802.11 physical limits
DEFAULT_ANCHORS = {
    "snr": {"min": 5.0, "max": 45.0},
    "noise": {"min": -100.0, "max": -75.0},
    "data_rate": {"min": 6.0, "max": 54.0},
}

DEFAULT_WEIGHTS = {
    "w_snr": 0.40,
    "w_stability": 0.25,
    "w_noise": 0.20,
    "w_rate": 0.15,
}


def rank_channels_for_link(
    df_summaries: pd.DataFrame,
    section: str,
    link_id: int,
    weights: Optional[Dict[str, float]] = None,
    anchors: Optional[Dict[str, Dict[str, float]]] = None,
) -> List[Dict[str, Any]]:
    """Rank all available channels for a given link within a section."""
    if weights is None:
        weights = DEFAULT_WEIGHTS
    if anchors is None:
        anchors = DEFAULT_ANCHORS

    subset = df_summaries[
        (df_summaries["section"] == section) & (df_summaries["link_id"] == link_id)
    ]
    if subset.empty:
        return []

    ranked = []
    for _, row in subset.iterrows():
        snr_mean = float(row["snr_mean"])
        snr_std = float(row["snr_std"])
        snr_stability = 1.0 / (1.0 + snr_std)
        noise_mean = float(row["noise_mean"])
        data_rate = float(row["data_rate_mode"])

        scoring = calculate_rank_score(
            snr_mean=snr_mean,
            snr_stability=snr_stability,
            noise_mean=noise_mean,
            data_rate=data_rate,
            weights=weights,
            anchors=anchors,
        )

        ranked.append({
            "channel": int(row["channel"]),
            "record_count": int(row["record_count"]),
            "snr_mean": snr_mean,
            "snr_std": snr_std,
            "snr_median": float(row["snr_median"]),
            "rss_mean": float(row["rss_mean"]),
            "noise_mean": noise_mean,
            "data_rate": data_rate,
            "score": scoring["score"],
            "breakdown": scoring["breakdown"],
            "normalized_features": scoring["normalized_features"],
        })

    # Sort descending by score
    ranked.sort(key=lambda x: x["score"], reverse=True)

    # Assign rank indices and compute baseline comparative ranks
    # Baselines: Highest median SNR, Highest mean RSS, Lowest noise
    sorted_by_snr_med = sorted(ranked, key=lambda x: x["snr_median"], reverse=True)
    sorted_by_rss = sorted(ranked, key=lambda x: x["rss_mean"], reverse=True)
    sorted_by_noise = sorted(ranked, key=lambda x: x["noise_mean"])  # lower noise is better

    for i, item in enumerate(ranked):
        item["rank"] = i + 1
        item["baseline_snr_rank"] = next(idx + 1 for idx, x in enumerate(sorted_by_snr_med) if x["channel"] == item["channel"])
        item["baseline_rss_rank"] = next(idx + 1 for idx, x in enumerate(sorted_by_rss) if x["channel"] == item["channel"])
        item["baseline_noise_rank"] = next(idx + 1 for idx, x in enumerate(sorted_by_noise) if x["channel"] == item["channel"])

    return ranked

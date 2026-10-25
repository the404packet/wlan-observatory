"""Unit tests for explainable channel ranking engine."""
import pandas as pd
import pytest
from src.pipeline.ranking import DEFAULT_ANCHORS, DEFAULT_WEIGHTS, rank_channels_for_link


def test_ranking_sorting_and_baselines():
    # Synthetic test DataFrame of summaries
    data = [
        {
            "section": "802_11a",
            "link_id": 0,
            "channel": 36,
            "record_count": 1000,
            "snr_mean": 25.0,
            "snr_std": 1.5,
            "snr_median": 25.0,
            "rss_mean": -70.0,
            "rss_std": 2.0,
            "rss_median": -70.0,
            "noise_mean": -95.0,
            "noise_std": 1.0,
            "data_rate_mode": 6.0,
            "seq_gap_count": 5,
            "seq_anomaly_ratio": 0.005,
            "duration_us": 100000.0,
        },
        {
            "section": "802_11a",
            "link_id": 0,
            "channel": 40,
            "record_count": 1000,
            "snr_mean": 12.0,
            "snr_std": 4.5,
            "snr_median": 12.0,
            "rss_mean": -83.0,
            "rss_std": 3.0,
            "rss_median": -83.0,
            "noise_mean": -95.0,
            "noise_std": 1.0,
            "data_rate_mode": 6.0,
            "seq_gap_count": 50,
            "seq_anomaly_ratio": 0.05,
            "duration_us": 100000.0,
        },
    ]
    df = pd.DataFrame(data)
    ranked = rank_channels_for_link(df, "802_11a", 0)

    assert len(ranked) == 2
    assert ranked[0]["channel"] == 36
    assert ranked[0]["rank"] == 1
    assert ranked[0]["score"] > ranked[1]["score"]
    assert "breakdown" in ranked[0]
    assert "baseline_snr_rank" in ranked[0]

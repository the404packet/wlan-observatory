"""Feature extraction and summary aggregation over CRAWDAD wireless trace files."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config import settings
from src.common.types import ChannelSummary

log = logging.getLogger(__name__)


def extract_file_features(
    file_path: Path,
    section: str,
    link_id: int,
    channel: int,
    max_rows: Optional[int] = None,
) -> Optional[ChannelSummary]:
    """Extract statistical summary metrics from a single raw trace CSV."""
    if not file_path.exists() or file_path.stat().st_size == 0:
        return None

    try:
        df = pd.read_csv(
            file_path,
            header=None,
            names=list(settings.EXPECTED_COLUMNS),
            nrows=max_rows,
            dtype={
                "timestamp": np.float64,
                "packet_type": str,
                "channel": np.int32,
                "snr": np.float64,
                "rss": np.float64,
                "noise": np.float64,
                "data_rate": np.float64,
                "seq": np.float64,
            },
        )
    except Exception as e:
        log.warning("Failed to parse file %s: %s", file_path, e)
        return None

    if len(df) == 0:
        return None

    record_count = len(df)
    snr_mean = float(df["snr"].mean())
    snr_std = float(df["snr"].std(ddof=1)) if record_count > 1 else 0.0
    snr_median = float(df["snr"].median())

    rss_mean = float(df["rss"].mean())
    rss_std = float(df["rss"].std(ddof=1)) if record_count > 1 else 0.0
    rss_median = float(df["rss"].median())

    noise_mean = float(df["noise"].mean())
    noise_std = float(df["noise"].std(ddof=1)) if record_count > 1 else 0.0

    # Data rate mode
    mode_vals = df["data_rate"].mode()
    data_rate_mode = float(mode_vals.iloc[0]) if len(mode_vals) > 0 else 0.0

    # Sequence gaps (12-bit wrap around 4096)
    seqs = df["seq"].dropna().to_numpy()
    seq_gaps = 0
    if len(seqs) > 1:
        diffs = (np.diff(seqs)) % 4096
        # A gap occurs when consecutive sequence counter differs by more than 1
        seq_gaps = int(np.sum(diffs > 1))

    seq_anomaly_ratio = float(seq_gaps / (record_count - 1)) if record_count > 1 else 0.0

    # Duration in microseconds
    t_min = df["timestamp"].min()
    t_max = df["timestamp"].max()
    duration_us = float(t_max - t_min) if pd.notnull(t_max) and pd.notnull(t_min) else 0.0

    return ChannelSummary(
        section=section,
        link_id=link_id,
        channel=channel,
        record_count=record_count,
        snr_mean=snr_mean,
        snr_std=snr_std,
        snr_median=snr_median,
        rss_mean=rss_mean,
        rss_std=rss_std,
        rss_median=rss_median,
        noise_mean=noise_mean,
        noise_std=noise_std,
        data_rate_mode=data_rate_mode,
        seq_gap_count=seq_gaps,
        seq_anomaly_ratio=seq_anomaly_ratio,
        duration_us=duration_us,
    )

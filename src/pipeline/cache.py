"""Cache manager for preprocessed summaries (Parquet / JSON)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from config import settings


def get_cache_path(name: str = "channel_summaries.parquet") -> Path:
    return settings.DATA_PROCESSED / name


def save_summaries_cache(df: pd.DataFrame, filename: str = "channel_summaries.parquet") -> Path:
    settings.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    out_path = get_cache_path(filename)
    df.to_parquet(out_path, index=False)
    # Also save a JSON copy for light web API reading
    json_path = settings.DATA_PROCESSED / filename.replace(".parquet", ".json")
    df.to_json(json_path, orient="records", indent=2)
    return out_path


def load_summaries_cache(filename: str = "channel_summaries.parquet") -> Optional[pd.DataFrame]:
    pq_path = get_cache_path(filename)
    if pq_path.exists():
        try:
            return pd.read_parquet(pq_path)
        except Exception:
            pass

    json_path = settings.DATA_PROCESSED / filename.replace(".parquet", ".json")
    if json_path.exists():
        return pd.read_json(json_path)

    return None

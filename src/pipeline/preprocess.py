"""Batch preprocessing of dataset into reusable summaries."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from config import settings
from src.pipeline.cache import save_summaries_cache
from src.pipeline.features import extract_file_features

log = logging.getLogger(__name__)


def preprocess_manifest_files(
    manifest_dir: Path = settings.DATA_MANIFESTS,
    dataset_dir: Path = settings.BASE_DIR / "dataset",
    sample_rows_per_file: Optional[int] = 1000,
) -> pd.DataFrame:
    """Preprocess all routed files into unified ChannelSummary records."""
    records = []
    for section in settings.SECTIONS:
        manifest_file = manifest_dir / f"{section}.manifest.json"
        if not manifest_file.exists():
            continue

        with open(manifest_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        for item in data.get("files", []):
            rel_path = item["path"]
            full_path = dataset_dir / rel_path
            link_id = item["link_id"]
            channel = item["channel_from_name"]
            if channel is None:
                # For interface files without channel in name, default channel is 64
                channel = 64

            summary = extract_file_features(
                file_path=full_path,
                section=section,
                link_id=link_id,
                channel=channel,
                max_rows=sample_rows_per_file,
            )
            if summary:
                records.append(summary.to_dict())

    df = pd.DataFrame(records)
    if not df.empty:
        save_summaries_cache(df)
    return df

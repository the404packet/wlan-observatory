"""Data catalogs, manifests and preprocessed cache retrieval service."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from config import settings
from src.pipeline.cache import load_summaries_cache
from src.pipeline.ranking import rank_channels_for_link
from src.pipeline.validate import audit_all_sections


class CatalogService:
    @staticmethod
    def get_dataset_overview() -> Dict[str, Any]:
        """Aggregate high level metrics across sections."""
        manifests = {}
        total_files = 0
        total_records = 0

        summaries_df = load_summaries_cache()
        has_cache = summaries_df is not None and not summaries_df.empty

        for section in settings.SECTIONS:
            m_path = settings.DATA_MANIFESTS / f"{section}.manifest.json"
            if m_path.exists():
                with open(m_path, "r", encoding="utf-8") as fh:
                    d = json.load(fh)
                    file_cnt = len(d.get("files", []))
                    manifests[section] = {
                        "files": file_cnt,
                        "expected": d.get("expected_file_count"),
                        "match": d.get("counts_match_expected"),
                        "built_at": d.get("built_at"),
                    }
                    total_files += file_cnt
            else:
                manifests[section] = {
                    "files": 0,
                    "expected": settings.EXPECTED_FILE_COUNTS.get(section),
                    "match": False,
                    "built_at": None,
                }

        if has_cache:
            total_records = int(summaries_df["record_count"].sum())

        return {
            "total_files": total_files,
            "total_records": total_records,
            "has_cache": has_cache,
            "manifests": manifests,
        }

    @staticmethod
    def get_channel_summaries(section: Optional[str] = None, link_id: Optional[int] = None) -> List[Dict[str, Any]]:
        df = load_summaries_cache()
        if df is None or df.empty:
            return []

        if section:
            df = df[df["section"] == section]
        if link_id is not None:
            df = df[df["link_id"] == link_id]

        return df.to_dict(orient="records")

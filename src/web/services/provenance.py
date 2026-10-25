"""Provenance management and registry service."""
from __future__ import annotations

from typing import Any, Dict
import yaml

from config import settings
from src.common.provenance import load_registry, registry, tag


def get_provenance_registry() -> Dict[str, Any]:
    prov_path = settings.BASE_DIR / "config" / "provenance.yaml"
    with open(prov_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)

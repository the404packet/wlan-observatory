"""Provenance registry: single source of truth for metric classification."""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class Provenance(str, enum.Enum):
    MEASURED = "MEASURED"
    DERIVED = "DERIVED"
    ASSUMED = "ASSUMED"
    SIMULATED = "SIMULATED"


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: Any
    provenance: Provenance
    source: str = ""
    n: int | None = None
    ci: tuple[float, float] | None = None
    assumptions: tuple[str, ...] = field(default_factory=tuple)


_REGISTRY: dict[str, dict[str, Any]] | None = None


def load_registry(path: str | Path) -> dict[str, dict[str, Any]]:
    global _REGISTRY
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if "metrics" not in raw or not raw["metrics"]:
        raise ValueError(f"provenance registry at {path} contains no metrics")
    _REGISTRY = raw["metrics"]
    return _REGISTRY


def registry() -> dict[str, dict[str, Any]]:
    if _REGISTRY is None:
        raise RuntimeError("Provenance registry not loaded. Call load_registry() first.")
    return _REGISTRY


def tag(name: str, value: Any, **kwargs: Any) -> MetricResult:
    """Build a MetricResult. Raises if the metric is not registered.

    This is the guardrail that prevents fabricated metrics from reaching the UI:
    every metric shown must be declared in provenance.yaml.
    """
    reg = registry()
    if name not in reg:
        raise KeyError(
            f"Metric {name!r} is not registered in provenance.yaml. "
            f"Register it before using it, or do not surface it in the UI."
        )
    entry = reg[name]
    prov = Provenance(entry["class"])
    return MetricResult(
        name=name,
        value=value,
        provenance=prov,
        source=entry.get("source", ""),
        n=kwargs.get("n"),
        ci=kwargs.get("ci"),
        assumptions=tuple(entry.get("assumptions", ())) + tuple(kwargs.get("assumptions", ())),
    )
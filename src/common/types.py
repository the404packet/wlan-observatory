"""Common data types and domain models for WLAN Observatory."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class Provenance(str, Enum):
    MEASURED = "MEASURED"
    DERIVED = "DERIVED"
    ASSUMED = "ASSUMED"
    SIMULATED = "SIMULATED"


@dataclass(frozen=True)
class MetricValue:
    name: str
    value: Any
    provenance: Provenance
    source: str = ""
    n: Optional[int] = None
    ci: Optional[Tuple[float, float]] = None
    assumptions: Tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "provenance": self.provenance.value,
            "source": self.source,
            "n": self.n,
            "ci": list(self.ci) if self.ci else None,
            "assumptions": list(self.assumptions),
        }


@dataclass
class ChannelSummary:
    section: str
    link_id: int
    channel: int
    record_count: int
    snr_mean: float
    snr_std: float
    snr_median: float
    rss_mean: float
    rss_std: float
    rss_median: float
    noise_mean: float
    noise_std: float
    data_rate_mode: float
    seq_gap_count: int
    seq_anomaly_ratio: float
    duration_us: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section": self.section,
            "link_id": self.link_id,
            "channel": self.channel,
            "record_count": self.record_count,
            "snr_mean": round(self.snr_mean, 2),
            "snr_std": round(self.snr_std, 2),
            "snr_median": round(self.snr_median, 2),
            "rss_mean": round(self.rss_mean, 2),
            "rss_std": round(self.rss_std, 2),
            "rss_median": round(self.rss_median, 2),
            "noise_mean": round(self.noise_mean, 2),
            "noise_std": round(self.noise_std, 2),
            "data_rate_mode": round(self.data_rate_mode, 1),
            "seq_gap_count": int(self.seq_gap_count),
            "seq_anomaly_ratio": round(self.seq_anomaly_ratio, 4),
            "duration_us": self.duration_us,
        }

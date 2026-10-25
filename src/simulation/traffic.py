"""Traffic generation models for wireless nodes."""
from __future__ import annotations

from enum import Enum
import random


class TrafficPattern(str, Enum):
    SATURATED = "SATURATED"
    POISSON = "POISSON"


class TrafficSource:
    def __init__(self, pattern: TrafficPattern = TrafficPattern.SATURATED, rate_pkts_per_sec: float = 100.0):
        self.pattern = pattern
        self.rate_pkts_per_sec = rate_pkts_per_sec
        self.has_packet = True
        self.next_arrival_time_us = 0.0

    def check_has_packet(self, current_time_us: float, rng: random.Random) -> bool:
        if self.pattern == TrafficPattern.SATURATED:
            return True
        if self.has_packet:
            return True
        if current_time_us >= self.next_arrival_time_us:
            self.has_packet = True
            # schedule next packet
            inter_arrival_sec = rng.expovariate(self.rate_pkts_per_sec)
            self.next_arrival_time_us = current_time_us + (inter_arrival_sec * 1e6)
            return True
        return False

    def consume_packet(self, current_time_us: float, rng: random.Random) -> None:
        if self.pattern == TrafficPattern.SATURATED:
            self.has_packet = True
        else:
            self.has_packet = False
            inter_arrival_sec = rng.expovariate(self.rate_pkts_per_sec)
            self.next_arrival_time_us = current_time_us + (inter_arrival_sec * 1e6)

"""Validated discrete-event CSMA/CA DCF simulation engine."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from src.analysis.stats import jains_fairness_index
from src.simulation.backoff import BackoffState, BackoffStrategy
from src.simulation.rts_cts import calculate_transmission_durations
from src.simulation.traffic import TrafficPattern, TrafficSource


class EventType(str, Enum):
    IDLE = "IDLE"
    SUCCESS = "SUCCESS"
    COLLISION = "COLLISION"
    DROP = "DROP"


@dataclass
class SimEvent:
    start_time_us: float
    duration_us: float
    event_type: EventType
    transmitting_stations: List[int]
    station_counters: Dict[int, int]
    reason: str


@dataclass
class StationRecord:
    station_id: int
    successful_transmissions: int = 0
    collisions: int = 0
    retransmissions: int = 0
    dropped_packets: int = 0
    payload_bytes_delivered: int = 0
    delays_us: List[float] = field(default_factory=list)
    retry_stages: List[int] = field(default_factory=list)  # retries per delivered packet


class CsmaSimulator:
    def __init__(
        self,
        n_stations: int = 5,
        cw_min: int = 15,
        cw_max: int = 1023,
        backoff_strategy: BackoffStrategy = BackoffStrategy.BEB,
        payload_bytes: int = 1000,
        data_rate_mbps: float = 6.0,
        rts_cts: bool = False,
        frame_error_prob: float = 0.0,
        retry_limit: int = 7,
        traffic_pattern: TrafficPattern = TrafficPattern.SATURATED,
        poisson_rate: float = 100.0,
        seed: Optional[int] = 42,
    ):
        self.n_stations = n_stations
        self.cw_min = cw_min
        self.cw_max = cw_max
        self.backoff_strategy = backoff_strategy
        self.payload_bytes = payload_bytes
        self.data_rate_mbps = data_rate_mbps
        self.rts_cts = rts_cts
        self.frame_error_prob = frame_error_prob
        self.retry_limit = retry_limit
        self.traffic_pattern = traffic_pattern
        self.poisson_rate = poisson_rate
        self.seed = seed

        self.rng = random.Random(seed)

        self.stations = [
            BackoffState(
                cw_min=cw_min,
                cw_max=cw_max,
                retry_limit=retry_limit,
                strategy=backoff_strategy,
            )
            for _ in range(n_stations)
        ]
        self.traffic_sources = [
            TrafficSource(traffic_pattern, poisson_rate) for _ in range(n_stations)
        ]
        self.stats = [StationRecord(station_id=i) for i in range(n_stations)]
        self.packet_enqueued_time = [0.0 for _ in range(n_stations)]
        self.packet_retry_count = [0 for _ in range(n_stations)]  # track retries per in-flight pkt

        # Initialize backoffs
        for s in self.stations:
            s.reset_cw(self.rng)

        self.timings = calculate_transmission_durations(
            payload_bytes=payload_bytes,
            data_rate_mbps=data_rate_mbps,
            rts_cts=rts_cts,
        )

        self.current_time_us = 0.0
        self.timeline: List[SimEvent] = []

        # Channel time accounting
        self.time_in_success_us = 0.0
        self.time_in_collision_us = 0.0
        self.time_in_idle_us = 0.0

    def run(self, max_events: int = 1000, max_duration_us: Optional[float] = None) -> Dict[str, Any]:
        """Execute DCF countdown and event resolution."""
        slot_time = self.timings["slot_time_us"]
        event_count = 0
        TIMELINE_LIMIT = 200  # store up to 200 events for visualization

        while event_count < max_events:
            if max_duration_us is not None and self.current_time_us >= max_duration_us:
                break

            ready_stations = [
                i for i in range(self.n_stations)
                if self.traffic_sources[i].check_has_packet(self.current_time_us, self.rng)
            ]

            if not ready_stations:
                # No traffic at all
                self.time_in_idle_us += slot_time
                if len(self.timeline) < TIMELINE_LIMIT:
                    self.timeline.append(SimEvent(
                        start_time_us=self.current_time_us,
                        duration_us=slot_time,
                        event_type=EventType.IDLE,
                        transmitting_stations=[],
                        station_counters={i: self.stations[i].backoff_counter for i in range(self.n_stations)},
                        reason="No traffic queued",
                    ))
                self.current_time_us += slot_time
                event_count += 1
                continue

            transmitters = [
                i for i in ready_stations if self.stations[i].backoff_counter == 0
            ]

            if not transmitters:
                # Idle slot: decrement all ready station counters
                counters_snapshot = {i: self.stations[i].backoff_counter for i in range(self.n_stations)}
                for i in ready_stations:
                    self.stations[i].decrement()
                self.time_in_idle_us += slot_time
                if len(self.timeline) < TIMELINE_LIMIT:
                    self.timeline.append(SimEvent(
                        start_time_us=self.current_time_us,
                        duration_us=slot_time,
                        event_type=EventType.IDLE,
                        transmitting_stations=[],
                        station_counters=counters_snapshot,
                        reason="Slot countdown: channel idle",
                    ))
                self.current_time_us += slot_time
                event_count += 1
                continue

            # Transmission attempt(s)
            station_counters = {i: self.stations[i].backoff_counter for i in range(self.n_stations)}

            if len(transmitters) == 1:
                st = transmitters[0]
                is_frame_error = (self.rng.random() < self.frame_error_prob)

                if not is_frame_error:
                    duration = self.timings["t_succ_us"]
                    self.stats[st].successful_transmissions += 1
                    self.stats[st].payload_bytes_delivered += self.payload_bytes
                    self.stats[st].retry_stages.append(self.packet_retry_count[st])

                    access_delay = self.current_time_us + duration - self.packet_enqueued_time[st]
                    self.stats[st].delays_us.append(access_delay)

                    self.stations[st].reset_cw(self.rng)
                    self.traffic_sources[st].consume_packet(self.current_time_us + duration, self.rng)
                    self.packet_enqueued_time[st] = self.current_time_us + duration
                    self.packet_retry_count[st] = 0

                    self.time_in_success_us += duration
                    if len(self.timeline) < TIMELINE_LIMIT:
                        self.timeline.append(SimEvent(
                            start_time_us=self.current_time_us,
                            duration_us=duration,
                            event_type=EventType.SUCCESS,
                            transmitting_stations=[st],
                            station_counters=station_counters,
                            reason=f"Station {st} transmitted successfully (ACK received)",
                        ))
                    self.current_time_us += duration
                else:
                    duration = self.timings["t_coll_us"]
                    self.packet_retry_count[st] += 1
                    retained = self.stations[st].double_cw_on_failure(self.rng)
                    self.stats[st].retransmissions += 1

                    if not retained:
                        self.stats[st].dropped_packets += 1
                        self.traffic_sources[st].consume_packet(self.current_time_us + duration, self.rng)
                        self.packet_enqueued_time[st] = self.current_time_us + duration
                        self.packet_retry_count[st] = 0

                    self.time_in_collision_us += duration
                    if len(self.timeline) < TIMELINE_LIMIT:
                        self.timeline.append(SimEvent(
                            start_time_us=self.current_time_us,
                            duration_us=duration,
                            event_type=EventType.DROP if not retained else EventType.COLLISION,
                            transmitting_stations=[st],
                            station_counters=station_counters,
                            reason=f"Station {st} frame corrupted (FER={self.frame_error_prob})",
                        ))
                    self.current_time_us += duration

            else:
                # COLLISION
                duration = self.timings["t_coll_us"]
                for st in transmitters:
                    self.stats[st].collisions += 1
                    self.packet_retry_count[st] += 1
                    retained = self.stations[st].double_cw_on_failure(self.rng)
                    if not retained:
                        self.stats[st].dropped_packets += 1
                        self.traffic_sources[st].consume_packet(self.current_time_us + duration, self.rng)
                        self.packet_enqueued_time[st] = self.current_time_us + duration
                        self.packet_retry_count[st] = 0

                self.time_in_collision_us += duration
                if len(self.timeline) < TIMELINE_LIMIT:
                    self.timeline.append(SimEvent(
                        start_time_us=self.current_time_us,
                        duration_us=duration,
                        event_type=EventType.COLLISION,
                        transmitting_stations=transmitters,
                        station_counters=station_counters,
                        reason=f"Collision between stations {transmitters}",
                    ))
                self.current_time_us += duration

            event_count += 1

        return self._compile_results()

    def _compile_results(self) -> Dict[str, Any]:
        total_time_sec = self.current_time_us / 1e6
        total_payload_bytes = sum(s.payload_bytes_delivered for s in self.stats)
        total_payload_bits = total_payload_bytes * 8.0

        throughput_mbps = (total_payload_bits / total_time_sec / 1e6) if total_time_sec > 0 else 0.0
        max_possible_bits = total_time_sec * self.data_rate_mbps * 1e6
        norm_throughput = (total_payload_bits / max_possible_bits) if max_possible_bits > 0 else 0.0

        total_tx_attempts = sum(s.successful_transmissions + s.collisions for s in self.stats)
        total_collisions = sum(s.collisions for s in self.stats)
        total_drops = sum(s.dropped_packets for s in self.stats)
        collision_prob = (total_collisions / total_tx_attempts) if total_tx_attempts > 0 else 0.0
        drop_rate = (total_drops / (total_tx_attempts + 1e-6)) if total_tx_attempts > 0 else 0.0

        # Delays
        all_delays = [d for s in self.stats for d in s.delays_us]
        mean_delay_ms = (float(np.mean(all_delays)) / 1000.0) if all_delays else 0.0
        p95_delay_ms = (float(np.percentile(all_delays, 95)) / 1000.0) if all_delays else 0.0

        # Delay histogram (20 bins)
        delay_hist = {"bins": [], "counts": []}
        if all_delays:
            counts, bin_edges = np.histogram(all_delays, bins=20)
            delay_hist = {
                "bins": [round(float(b) / 1000.0, 3) for b in bin_edges],
                "counts": [int(c) for c in counts],
            }

        station_throughputs = [
            (s.payload_bytes_delivered * 8.0 / total_time_sec / 1e6) if total_time_sec > 0 else 0.0
            for s in self.stats
        ]
        fairness = jains_fairness_index(station_throughputs)

        # Per-station collision and success counts
        per_station_collisions = [s.collisions for s in self.stats]
        per_station_success = [s.successful_transmissions for s in self.stats]
        per_station_drops = [s.dropped_packets for s in self.stats]

        # Retry stage distribution: how many packets needed 0, 1, 2, 3+ retries
        all_retries = [r for s in self.stats for r in s.retry_stages]
        retry_dist = {}
        for r in all_retries:
            key = str(min(r, 7))
            retry_dist[key] = retry_dist.get(key, 0) + 1

        # Channel efficiency breakdown (microseconds → percentage)
        total_accounted = self.time_in_success_us + self.time_in_collision_us + self.time_in_idle_us
        if total_accounted > 0:
            eff_success_pct = round(self.time_in_success_us / total_accounted * 100, 2)
            eff_collision_pct = round(self.time_in_collision_us / total_accounted * 100, 2)
            eff_idle_pct = round(self.time_in_idle_us / total_accounted * 100, 2)
        else:
            eff_success_pct = eff_collision_pct = eff_idle_pct = 0.0

        return {
            "config": {
                "n_stations": self.n_stations,
                "cw_min": self.cw_min,
                "cw_max": self.cw_max,
                "backoff_strategy": self.backoff_strategy.value,
                "payload_bytes": self.payload_bytes,
                "data_rate_mbps": self.data_rate_mbps,
                "rts_cts": self.rts_cts,
                "frame_error_prob": self.frame_error_prob,
                "retry_limit": self.retry_limit,
                "seed": self.seed,
            },
            "metrics": {
                "aggregate_throughput_mbps": round(float(throughput_mbps), 3),
                "normalized_throughput": round(float(norm_throughput), 4),
                "collision_probability": round(float(collision_prob), 4),
                "packet_drop_rate": round(float(drop_rate), 4),
                "mean_access_delay_ms": round(float(mean_delay_ms), 3),
                "p95_access_delay_ms": round(float(p95_delay_ms), 3),
                "jains_fairness_index": round(float(fairness), 4),
                "total_sim_time_ms": round(float(self.current_time_us / 1000.0), 2),
                "total_events": event_count if False else len(self.timeline),
                "per_station_throughput_mbps": [round(float(th), 3) for th in station_throughputs],
                "per_station_collisions": per_station_collisions,
                "per_station_success": per_station_success,
                "per_station_drops": per_station_drops,
            },
            "channel_efficiency": {
                "success_pct": eff_success_pct,
                "collision_pct": eff_collision_pct,
                "idle_pct": eff_idle_pct,
                "success_us": round(self.time_in_success_us, 1),
                "collision_us": round(self.time_in_collision_us, 1),
                "idle_us": round(self.time_in_idle_us, 1),
            },
            "delay_histogram": delay_hist,
            "retry_distribution": retry_dist,
            "timeline": [
                {
                    "start_time_us": round(e.start_time_us, 1),
                    "duration_us": round(e.duration_us, 1),
                    "type": e.event_type.value,
                    "stations": e.transmitting_stations,
                    "counters": e.station_counters,
                    "reason": e.reason,
                }
                for e in self.timeline
            ],
        }

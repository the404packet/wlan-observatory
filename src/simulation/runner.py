"""Runner for Monte Carlo replications, sweeps and strategy comparisons."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from config import settings
from src.analysis.stats import mean_confidence_interval
from src.simulation.backoff import BackoffStrategy
from src.simulation.engine import CsmaSimulator
from src.simulation.traffic import TrafficPattern


def run_experiment_replications(
    n_replications: int = 5,
    n_stations: int = 5,
    cw_min: int = 15,
    cw_max: int = 1023,
    backoff_strategy: str = "BEB",
    payload_bytes: int = 1000,
    data_rate_mbps: float = 6.0,
    rts_cts: bool = False,
    frame_error_prob: float = 0.0,
    retry_limit: int = 7,
    traffic_pattern: str = "SATURATED",
    poisson_rate: float = 100.0,
    max_events: int = 1000,
    base_seed: int = 42,
) -> Dict[str, Any]:
    """Execute multiple Monte Carlo replications and aggregate with 95% CIs."""
    strategy_enum = BackoffStrategy(backoff_strategy)
    traffic_enum = TrafficPattern(traffic_pattern)

    rep_results = []
    throughputs, collision_probs, delays, fairnesses = [], [], [], []
    last_run_full = None

    for i in range(n_replications):
        seed = base_seed + (i * 1001)
        sim = CsmaSimulator(
            n_stations=n_stations, cw_min=cw_min, cw_max=cw_max,
            backoff_strategy=strategy_enum, payload_bytes=payload_bytes,
            data_rate_mbps=data_rate_mbps, rts_cts=rts_cts,
            frame_error_prob=frame_error_prob, retry_limit=retry_limit,
            traffic_pattern=traffic_enum, poisson_rate=poisson_rate, seed=seed,
        )
        res = sim.run(max_events=max_events)
        rep_results.append(res["metrics"])
        throughputs.append(res["metrics"]["aggregate_throughput_mbps"])
        collision_probs.append(res["metrics"]["collision_probability"])
        delays.append(res["metrics"]["mean_access_delay_ms"])
        fairnesses.append(res["metrics"]["jains_fairness_index"])
        if i == 0:
            last_run_full = res

    def ci(data):
        m, lo, hi = mean_confidence_interval(data)
        return {"mean": round(m, 4), "ci_lower": round(lo, 4), "ci_upper": round(hi, 4)}

    return {
        "config": {
            "n_replications": n_replications, "n_stations": n_stations,
            "cw_min": cw_min, "cw_max": cw_max, "backoff_strategy": backoff_strategy,
            "payload_bytes": payload_bytes, "data_rate_mbps": data_rate_mbps,
            "rts_cts": rts_cts, "frame_error_prob": frame_error_prob,
            "retry_limit": retry_limit, "traffic_pattern": traffic_pattern,
            "poisson_rate": poisson_rate, "max_events": max_events, "base_seed": base_seed,
        },
        "aggregated": {
            "throughput_mbps": ci(throughputs),
            "collision_probability": ci(collision_probs),
            "mean_access_delay_ms": ci(delays),
            "jains_fairness_index": ci(fairnesses),
        },
        "sample_timeline": last_run_full["timeline"] if last_run_full else [],
        "channel_efficiency": last_run_full["channel_efficiency"] if last_run_full else {},
        "delay_histogram": last_run_full["delay_histogram"] if last_run_full else {},
        "retry_distribution": last_run_full["retry_distribution"] if last_run_full else {},
        "replications": rep_results,
    }


def run_station_sweep(
    station_counts: Optional[List[int]] = None,
    cw_min: int = 15,
    cw_max: int = 1023,
    backoff_strategy: str = "BEB",
    payload_bytes: int = 1000,
    data_rate_mbps: float = 6.0,
    rts_cts: bool = False,
    frame_error_prob: float = 0.0,
    n_replications: int = 3,
    max_events: int = 800,
) -> Dict[str, Any]:
    """Sweep N from station_counts and record throughput + collision probability at each point."""
    if station_counts is None:
        station_counts = [1, 2, 3, 5, 8, 10, 15, 20, 25, 30]

    sweep_points = []
    for n in station_counts:
        res = run_experiment_replications(
            n_replications=n_replications, n_stations=n,
            cw_min=cw_min, cw_max=cw_max, backoff_strategy=backoff_strategy,
            payload_bytes=payload_bytes, data_rate_mbps=data_rate_mbps,
            rts_cts=rts_cts, frame_error_prob=frame_error_prob,
            max_events=max_events,
        )
        sweep_points.append({
            "n_stations": n,
            "throughput_mbps": res["aggregated"]["throughput_mbps"],
            "collision_probability": res["aggregated"]["collision_probability"],
            "jains_fairness_index": res["aggregated"]["jains_fairness_index"],
            "mean_access_delay_ms": res["aggregated"]["mean_access_delay_ms"],
        })

    return {
        "config": {
            "cw_min": cw_min, "cw_max": cw_max, "backoff_strategy": backoff_strategy,
            "payload_bytes": payload_bytes, "data_rate_mbps": data_rate_mbps,
            "rts_cts": rts_cts, "frame_error_prob": frame_error_prob,
            "n_replications": n_replications,
        },
        "sweep": sweep_points,
    }


def run_strategy_comparison(
    n_stations: int = 10,
    cw_min: int = 15,
    cw_max: int = 1023,
    payload_bytes: int = 1000,
    data_rate_mbps: float = 6.0,
    rts_cts: bool = False,
    n_replications: int = 3,
    max_events: int = 800,
) -> Dict[str, Any]:
    """Compare BEB vs Fixed CW under identical conditions."""
    beb = run_experiment_replications(
        n_replications=n_replications, n_stations=n_stations,
        cw_min=cw_min, cw_max=cw_max, backoff_strategy="BEB",
        payload_bytes=payload_bytes, data_rate_mbps=data_rate_mbps,
        rts_cts=rts_cts, max_events=max_events,
    )
    fixed = run_experiment_replications(
        n_replications=n_replications, n_stations=n_stations,
        cw_min=cw_min, cw_max=cw_max, backoff_strategy="FIXED",
        payload_bytes=payload_bytes, data_rate_mbps=data_rate_mbps,
        rts_cts=rts_cts, max_events=max_events,
    )
    return {
        "config": {
            "n_stations": n_stations, "cw_min": cw_min, "cw_max": cw_max,
            "payload_bytes": payload_bytes, "data_rate_mbps": data_rate_mbps,
            "rts_cts": rts_cts,
        },
        "BEB": beb["aggregated"],
        "FIXED": fixed["aggregated"],
        "BEB_efficiency": beb.get("channel_efficiency", {}),
        "FIXED_efficiency": fixed.get("channel_efficiency", {}),
        "BEB_retry_dist": beb.get("retry_distribution", {}),
        "FIXED_retry_dist": fixed.get("retry_distribution", {}),
    }


def save_experiment_run(run_id: str, data: Dict[str, Any]) -> Path:
    settings.DATA_SIM_RUNS.mkdir(parents=True, exist_ok=True)
    out_file = settings.DATA_SIM_RUNS / f"{run_id}.json"
    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return out_file


def list_saved_experiments() -> List[Dict[str, Any]]:
    settings.DATA_SIM_RUNS.mkdir(parents=True, exist_ok=True)
    experiments = []
    for f in settings.DATA_SIM_RUNS.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                experiments.append({
                    "id": f.stem,
                    "filename": f.name,
                    "config": data.get("config", {}),
                    "aggregated": data.get("aggregated", {}),
                })
        except Exception:
            continue
    return sorted(experiments, key=lambda x: x["id"], reverse=True)

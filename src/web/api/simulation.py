"""CSMA/CA Simulation and Bianchi analytical validation API endpoints."""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request

from src.simulation.bianchi import compute_bianchi_throughput
from src.simulation.runner import (
    list_saved_experiments,
    run_experiment_replications,
    save_experiment_run,
)

sim_bp = Blueprint("simulation", __name__, url_prefix="/api/simulation")


@sim_bp.route("/run", methods=["POST"])
def run_simulation():
    body = request.get_json() or {}

    n_stations = int(body.get("n_stations", 5))
    cw_min = int(body.get("cw_min", 15))
    cw_max = int(body.get("cw_max", 1023))
    strategy = str(body.get("backoff_strategy", "BEB"))
    payload = int(body.get("payload_bytes", 1000))
    data_rate = float(body.get("data_rate_mbps", 6.0))
    rts_cts = bool(body.get("rts_cts", False))
    frame_error_prob = float(body.get("frame_error_prob", 0.0))
    retry_limit = int(body.get("retry_limit", 7))
    traffic = str(body.get("traffic_pattern", "SATURATED"))
    poisson_rate = float(body.get("poisson_rate", 100.0))
    replications = int(body.get("n_replications", 3))
    max_events = int(body.get("max_events", 1000))

    results = run_experiment_replications(
        n_replications=replications,
        n_stations=n_stations,
        cw_min=cw_min,
        cw_max=cw_max,
        backoff_strategy=strategy,
        payload_bytes=payload,
        data_rate_mbps=data_rate,
        rts_cts=rts_cts,
        frame_error_prob=frame_error_prob,
        retry_limit=retry_limit,
        traffic_pattern=traffic,
        poisson_rate=poisson_rate,
        max_events=max_events,
    )

    return jsonify({
        "status": "success",
        "data": results,
        "provenance": {
            "aggregate_throughput_mbps": "SIMULATED",
            "collision_probability": "SIMULATED",
            "access_delay": "SIMULATED",
            "frame_error_prob": "ASSUMED",
        }
    })


@sim_bp.route("/bianchi", methods=["POST"])
def validate_bianchi():
    body = request.get_json() or {}

    cw_min = int(body.get("cw_min", 15))
    cw_max = int(body.get("cw_max", 1023))
    payload_bytes = int(body.get("payload_bytes", 1000))
    data_rate = float(body.get("data_rate_mbps", 6.0))
    rts_cts = bool(body.get("rts_cts", False))
    stations_list = body.get("stations", [2, 5, 10, 15, 20, 25])

    comparison = []
    for n in stations_list:
        analytical = compute_bianchi_throughput(
            n_stations=n,
            cw_min=cw_min,
            cw_max=cw_max,
            payload_bytes=payload_bytes,
            data_rate_mbps=data_rate,
            rts_cts=rts_cts,
        )

        # Run matched simulated replication
        sim_out = run_experiment_replications(
            n_replications=3,
            n_stations=n,
            cw_min=cw_min,
            cw_max=cw_max,
            backoff_strategy="BEB",
            payload_bytes=payload_bytes,
            data_rate_mbps=data_rate,
            rts_cts=rts_cts,
            frame_error_prob=0.0,  # Bianchi assumes error-free channel
            traffic_pattern="SATURATED",  # Bianchi assumes saturated queues
            max_events=800,
        )

        sim_th = sim_out["aggregated"]["throughput_mbps"]["mean"]
        sim_col = sim_out["aggregated"]["collision_probability"]["mean"]

        th_error_pct = round(abs(sim_th - analytical["throughput_mbps"]) / (analytical["throughput_mbps"] + 1e-6) * 100, 2)
        col_error_pct = round(abs(sim_col - analytical["collision_prob"]) / (analytical["collision_prob"] + 1e-6) * 100, 2)

        comparison.append({
            "stations": n,
            "analytical": analytical,
            "simulated": {
                "throughput_mbps": sim_th,
                "collision_probability": sim_col,
            },
            "discrepancy": {
                "throughput_error_pct": th_error_pct,
                "collision_error_pct": col_error_pct,
            }
        })

    return jsonify({
        "status": "success",
        "model": "Bianchi (2000) IEEE JSAC",
        "assumptions": [
            "Saturated traffic (queue always non-empty)",
            "Ideal channel conditions (frame error prob = 0.0)",
            "No hidden terminals (single broadcast collision domain)",
            "Constant collision probability independent of retransmission history",
        ],
        "comparison": comparison,
    })


@sim_bp.route("/experiments", methods=["GET"])
def get_experiments():
    exps = list_saved_experiments()
    return jsonify({"status": "success", "experiments": exps})


@sim_bp.route("/experiments/save", methods=["POST"])
def save_experiment():
    body = request.get_json() or {}
    run_id = body.get("name") or f"run_{uuid.uuid4().hex[:8]}"
    saved_path = save_experiment_run(run_id, body)
    return jsonify({"status": "success", "run_id": run_id, "path": str(saved_path)})

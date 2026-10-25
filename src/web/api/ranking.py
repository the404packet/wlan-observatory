"""Channel ranking and evaluation API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.pipeline.cache import load_summaries_cache
from src.pipeline.ranking import DEFAULT_ANCHORS, DEFAULT_WEIGHTS, rank_channels_for_link
from src.pipeline.uncertainty import run_sensitivity_analysis

ranking_bp = Blueprint("ranking", __name__, url_prefix="/api/ranking")


@ranking_bp.route("/evaluate", methods=["POST"])
def evaluate_ranking():
    payload = request.get_json() or {}
    section = payload.get("section", "802_11a")
    link_id = payload.get("link_id", 0)

    weights = payload.get("weights", DEFAULT_WEIGHTS)

    df = load_summaries_cache()
    if df is None or df.empty:
        return jsonify({"status": "error", "message": "Preprocessed summaries not found"}), 404

    ranked = rank_channels_for_link(
        df_summaries=df,
        section=section,
        link_id=link_id,
        weights=weights,
        anchors=DEFAULT_ANCHORS,
    )

    return jsonify({
        "status": "success",
        "section": section,
        "link_id": link_id,
        "weights": weights,
        "anchors": DEFAULT_ANCHORS,
        "rankings": ranked,
        "provenance": {
            "score": "DERIVED",
            "weights": "ASSUMED",
            "anchors": "ASSUMED",
        }
    })


@ranking_bp.route("/sensitivity", methods=["POST"])
def get_sensitivity():
    payload = request.get_json() or {}
    section = payload.get("section", "802_11a")
    link_id = payload.get("link_id", 0)
    weight_key = payload.get("weight_key", "w_snr")

    df = load_summaries_cache()
    if df is None or df.empty:
        return jsonify({"status": "error", "message": "Preprocessed summaries not found"}), 404

    res = run_sensitivity_analysis(
        df_summaries=df,
        section=section,
        link_id=link_id,
        weight_key=weight_key,
    )
    return jsonify({"status": "success", "data": res})

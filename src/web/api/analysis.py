"""Channel measurement analysis API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.pipeline.cache import load_summaries_cache
from src.web.services.catalog import CatalogService

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/analysis")


@analysis_bp.route("/summaries", methods=["GET"])
def get_summaries():
    section = request.args.get("section")
    link_id = request.args.get("link_id", type=int)

    data = CatalogService.get_channel_summaries(section=section, link_id=link_id)
    return jsonify({
        "status": "success",
        "count": len(data),
        "data": data,
        "provenance": {
            "rss_mean": "MEASURED",
            "noise_mean": "MEASURED",
            "snr_mean": "DERIVED",
            "data_rate_mode": "MEASURED",
            "seq_gap_count": "DERIVED",
        }
    })


@analysis_bp.route("/links", methods=["GET"])
def get_links():
    section = request.args.get("section", "802_11a")
    df = load_summaries_cache()
    if df is None or df.empty:
        return jsonify({"status": "success", "links": []})

    sub = df[df["section"] == section]
    links = sorted(sub["link_id"].unique().tolist())
    return jsonify({"status": "success", "section": section, "links": links})

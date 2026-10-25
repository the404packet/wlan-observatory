"""Provenance, Evidence and Exportable Report API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from config import settings
from src.pipeline.cache import load_summaries_cache
from src.pipeline.validate import audit_all_sections
from src.simulation.runner import list_saved_experiments
from src.web.services.provenance import get_provenance_registry

evidence_bp = Blueprint("evidence", __name__, url_prefix="/api/evidence")


@evidence_bp.route("/registry", methods=["GET"])
def get_registry():
    data = get_provenance_registry()
    return jsonify({"status": "success", "registry": data})


@evidence_bp.route("/report", methods=["GET"])
def generate_full_report():
    audits = audit_all_sections()
    df = load_summaries_cache()
    record_cnt = int(df["record_count"].sum()) if df is not None and not df.empty else 0
    channel_cnt = len(df) if df is not None and not df.empty else 0
    experiments = list_saved_experiments()
    prov_reg = get_provenance_registry()

    report = {
        "title": "Trace-Driven Channel Quality Ranking and Validated CSMA/CA Backoff Simulation for IEEE 802.11: A Provenance-Aware Analysis Tool",
        "dataset_summary": {
            "source": "CRAWDAD mesh-heterogeneity (Subramanian et al., PAM 2009)",
            "total_records_processed": record_cnt,
            "total_channels_analyzed": channel_cnt,
            "sections": ["802_11a", "802_11g", "interface"],
            "audits": audits,
        },
        "methodology": {
            "channel_ranking": "Multi-criteria normalized scoring with anchors for SNR, noise floor, stability and transmission rate.",
            "csma_simulation": "Discrete-event 802.11 DCF simulator implementing slot countdown, idle decrements, BEB/Fixed CW expansion and packet drops.",
            "bianchi_validation": "Non-linear numerical solver for conditional collision probability p and transmission probability tau under saturated queue assumptions.",
        },
        "provenance_ledger": prov_reg.get("metrics", {}),
        "scientific_disclaimers": [
            "Dataset records do not establish channel-busy time, CCA measurements, or actual collision counts.",
            "Packet counts must not be interpreted as channel utilization or airtime.",
            "Channel ranking scores reflect physical and receiver indicators, not MAC collision rates.",
            "CSMA/CA simulation results are purely SIMULATED models and must remain scientifically separate from empirical trace records.",
        ],
        "saved_simulations_count": len(experiments),
    }

    return jsonify({"status": "success", "report": report})

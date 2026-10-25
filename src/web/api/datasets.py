"""Datasets and validation API endpoints."""
from __future__ import annotations

import json
from flask import Blueprint, jsonify, request

from config import settings
from src.pipeline.validate import audit_all_sections, audit_section
from src.web.services.catalog import CatalogService

datasets_bp = Blueprint("datasets", __name__, url_prefix="/api/datasets")


@datasets_bp.route("/overview", methods=["GET"])
def dataset_overview():
    overview = CatalogService.get_dataset_overview()
    return jsonify({"status": "success", "data": overview})


@datasets_bp.route("/validation", methods=["GET"])
def dataset_validation():
    audits = audit_all_sections()
    return jsonify({"status": "success", "data": audits})


@datasets_bp.route("/manifests/<section>", methods=["GET"])
def get_manifest(section: str):
    path = settings.DATA_MANIFESTS / f"{section}.manifest.json"
    if not path.exists():
        return jsonify({"status": "error", "message": f"Manifest for section {section} not found"}), 404
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return jsonify({"status": "success", "data": data})

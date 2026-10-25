"""Flask Application initialization for WLAN Observatory."""
from __future__ import annotations

from pathlib import Path
from flask import Flask, redirect, render_template, url_for

from config import settings
from src.common.provenance import load_registry
from src.web.api.analysis import analysis_bp
from src.web.api.datasets import datasets_bp
from src.web.api.evidence import evidence_bp
from src.web.api.ranking import ranking_bp
from src.web.api.simulation import sim_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(settings.BASE_DIR / "templates"),
        static_folder=str(settings.BASE_DIR / "static"),
    )

    # Initialize directories and provenance registry
    settings.ensure_dirs()
    prov_path = settings.BASE_DIR / "config" / "provenance.yaml"
    if prov_path.exists():
        load_registry(prov_path)

    # Register API Blueprints
    app.register_blueprint(datasets_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(ranking_bp)
    app.register_blueprint(sim_bp)
    app.register_blueprint(evidence_bp)

    # UI Page Routes
    @app.route("/")
    def index():
        return redirect(url_for("overview"))

    @app.route("/overview")
    def overview():
        return render_template("pages/overview.html", page="overview")

    @app.route("/datasets")
    def datasets():
        return render_template("pages/datasets.html", page="datasets")

    @app.route("/channel-analysis")
    def channel_analysis():
        return render_template("pages/channel_analysis.html", page="channel_analysis")

    @app.route("/ranking-eval")
    def ranking_eval():
        return render_template("pages/ranking_eval.html", page="ranking_eval")

    @app.route("/simulator")
    def simulator():
        return render_template("pages/simulator.html", page="simulator")

    @app.route("/validation")
    def validation():
        return render_template("pages/comparison.html", page="validation")

    @app.route("/comparison")
    def comparison():
        return render_template("pages/comparison.html", page="comparison")

    @app.route("/evidence")
    def evidence():
        return render_template("pages/evidence.html", page="evidence")

    @app.route("/settings")
    def settings_page():
        return render_template("pages/settings.html", page="settings")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

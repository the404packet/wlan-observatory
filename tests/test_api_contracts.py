"""Integration and API Contract tests for WLAN Observatory Flask endpoints."""
import json
import pytest
from src.web.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_datasets_overview(client):
    res = client.get("/api/datasets/overview")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "total_files" in data["data"]


def test_api_datasets_validation(client):
    res = client.get("/api/datasets/validation")
    assert res.status_code == 200
    data = res.get_json()
    assert "802_11a" in data["data"]


def test_api_channel_summaries(client):
    res = client.get("/api/analysis/summaries?section=802_11a&link_id=0")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert isinstance(data["data"], list)


def test_api_ranking_evaluate(client):
    payload = {
        "section": "802_11a",
        "link_id": 0,
        "weights": {"w_snr": 0.4, "w_stability": 0.25, "w_noise": 0.2, "w_rate": 0.15},
    }
    res = client.post("/api/ranking/evaluate", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "rankings" in data


def test_api_simulation_run(client):
    payload = {
        "n_stations": 3,
        "cw_min": 15,
        "cw_max": 1023,
        "backoff_strategy": "BEB",
        "n_replications": 2,
        "max_events": 100,
    }
    res = client.post("/api/simulation/run", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "aggregated" in data["data"]
    assert "sample_timeline" in data["data"]


def test_api_bianchi_validation(client):
    payload = {
        "stations": [2, 5],
        "cw_min": 15,
        "cw_max": 1023,
    }
    res = client.post("/api/simulation/bianchi", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["comparison"]) == 2

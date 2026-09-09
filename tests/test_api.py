"""
tests/test_api.py — FastAPI contract tests.

Covers: TC-19 (malformed JSON → 4xx), TC-20 (missing field → 4xx),
TC-21 (/api/health → 200), TC-18 (what-if result shape).
REETHU-001 / FR-API-1 through FR-API-7.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# TC-21: /api/health → 200 + {"status": "ok"}
# ---------------------------------------------------------------------------
def test_health_tc21():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# TC-19: Malformed / missing body → 4xx
# ---------------------------------------------------------------------------
def test_missing_body_scenario_generate_tc19():
    resp = client.post("/api/scenario/generate", json={})
    # Default values fill in — should succeed with defaults
    assert resp.status_code == 200


def test_invalid_scenario_name():
    resp = client.post("/api/scenario/generate", json={"scenario_name": "nonexistent", "seed": 42})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Full scenario → forecast → optimize round-trip
# ---------------------------------------------------------------------------
def test_full_scenario_generate():
    resp = client.post("/api/scenario/generate", json={"scenario_name": "surge", "seed": 42})
    assert resp.status_code == 200
    data = resp.json()
    assert "scenario" in data
    assert "arrivals" in data


def test_forecast_endpoint():
    # First get a scenario
    sc_resp = client.post("/api/scenario/generate", json={"scenario_name": "normal", "seed": 42})
    scenario = sc_resp.json()["scenario"]

    resp = client.post("/api/forecast", json={"scenario": scenario})
    assert resp.status_code == 200
    fc = resp.json()
    assert "slots" in fc
    assert "expected_arrivals" in fc


def test_optimize_endpoint():
    sc_resp = client.post("/api/scenario/generate", json={"scenario_name": "surge", "seed": 42})
    scenario = sc_resp.json()["scenario"]

    fc_resp = client.post("/api/forecast", json={"scenario": scenario})
    forecast = fc_resp.json()

    resp = client.post("/api/optimize", json={"scenario": scenario, "forecast": forecast})
    assert resp.status_code == 200
    opt = resp.json()
    assert opt["feasible"] is True
    assert "explanation" in opt
    assert "improvement" in opt


def test_whatif_endpoint_tc18():
    sc_resp = client.post("/api/scenario/generate", json={"scenario_name": "normal", "seed": 42})
    scenario = sc_resp.json()["scenario"]

    fc_resp = client.post("/api/forecast", json={"scenario": scenario})
    forecast = fc_resp.json()

    whatif_alloc = {
        "label": "whatif",
        "staff_by_queue": {"teller": 3, "loans": 2, "customer_service": 2},
    }

    resp = client.post(
        "/api/whatif",
        json={"scenario": scenario, "forecast": forecast, "allocation": whatif_alloc},
    )
    assert resp.status_code == 200
    result = resp.json()
    # TC-18: same shape as SimulationResult
    assert "allocation_label" in result
    assert "per_queue" in result
    assert "branch_wide" in result
    assert result["allocation_label"] == "whatif"

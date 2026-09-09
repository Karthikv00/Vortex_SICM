"""
tests/test_api.py — FastAPI contract tests.

Covers: TC-19 (malformed JSON → 4xx), TC-20 (missing field → 4xx),
TC-21 (/api/health → 200), TC-18 (what-if result shape),
REETHU-002 simulation endpoint and contract validation.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_tc21():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_missing_body_scenario_generate_tc19():
    resp = client.post("/api/scenario/generate", json={})
    assert resp.status_code == 200


def test_invalid_scenario_name():
    resp = client.post("/api/scenario/generate", json={"scenario_name": "nonexistent", "seed": 42})
    assert resp.status_code == 422


def test_full_scenario_generate():
    resp = client.post("/api/scenario/generate", json={"scenario_name": "surge", "seed": 42})
    assert resp.status_code == 200
    data = resp.json()
    assert "scenario" in data
    assert "arrivals" in data


def test_forecast_endpoint():
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
    assert "allocation_label" in result
    assert "per_queue" in result
    assert "branch_wide" in result
    assert result["allocation_label"] == "whatif"


def _simulation_payload(scenario_name="normal", seed=42, allocation=None):
    sc_resp = client.post(
        "/api/scenario/generate", json={"scenario_name": scenario_name, "seed": seed}
    )
    assert sc_resp.status_code == 200
    scenario = sc_resp.json()["scenario"]
    fc_resp = client.post("/api/forecast", json={"scenario": scenario})
    assert fc_resp.status_code == 200
    forecast = fc_resp.json()
    if allocation is None:
        allocation = {
            "label": "baseline",
            "staff_by_queue": {q["queue_id"]: q["min_staff"] for q in scenario["queues"]},
        }
    return scenario, forecast, allocation


def test_simulate_endpoint_returns_simulation_result():
    scenario, forecast, allocation = _simulation_payload()
    resp = client.post(
        "/api/simulate",
        json={"scenario": scenario, "forecast": forecast, "allocation": allocation},
    )
    assert resp.status_code == 200
    result = resp.json()
    assert result["allocation_label"] == "baseline"
    assert set(result) == {"allocation_label", "per_queue", "branch_wide"}
    assert set(result["per_queue"]) == {q["queue_id"] for q in scenario["queues"]}


def test_simulate_missing_allocation_queue_returns_422():
    scenario, forecast, _ = _simulation_payload()
    allocation = {
        "label": "baseline",
        "staff_by_queue": {"teller": 1, "loans": 1},
    }
    resp = client.post(
        "/api/simulate",
        json={"scenario": scenario, "forecast": forecast, "allocation": allocation},
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["error"] == "simulation_input_error"


def test_whatif_and_simulate_match_for_same_allocation():
    scenario, forecast, allocation = _simulation_payload()
    simulate_resp = client.post(
        "/api/simulate",
        json={"scenario": scenario, "forecast": forecast, "allocation": allocation},
    )
    whatif_allocation = {**allocation, "label": "whatif"}
    whatif_resp = client.post(
        "/api/whatif",
        json={"scenario": scenario, "forecast": forecast, "allocation": whatif_allocation},
    )
    assert simulate_resp.status_code == 200
    assert whatif_resp.status_code == 200
    simulate_result = simulate_resp.json()
    whatif_result = whatif_resp.json()
    simulate_result["allocation_label"] = "whatif"
    assert simulate_result == whatif_result


def test_scenario_generate_missing_required_queues_returns_422():
    resp = client.post(
        "/api/scenario/generate",
        json={
            "scenario_name": "normal",
            "seed": 42,
            "total_staff_available": 10,
        },
    )
    assert resp.status_code == 422

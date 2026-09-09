"""
tests/test_api.py — FastAPI contract tests.

Covers: TC-19 (malformed JSON → 4xx), TC-20 (missing field → 4xx),
TC-21 (/api/health → 200), TC-18 (what-if result shape).
REETHU-001 / FR-API-1 through FR-API-7.
"""
from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app, raise_server_exceptions=False)


def _scenario_and_forecast() -> tuple[dict, dict]:
    scenario = client.post(
        "/api/scenario/generate", json={"scenario_name": "normal", "seed": 42}
    ).json()["scenario"]
    forecast = client.post("/api/forecast", json={"scenario": scenario}).json()
    return scenario, forecast


def _allocation(**overrides: int) -> dict:
    staff = {"teller": 3, "loans": 2, "customer_service": 2}
    staff.update(overrides)
    return {"label": "whatif", "staff_by_queue": staff}


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


def test_scenario_generate_rejects_missing_and_malformed_bodies():
    assert client.post("/api/scenario/generate").status_code == 422
    assert client.post(
        "/api/scenario/generate",
        content="{not json",
        headers={"content-type": "application/json"},
    ).status_code == 422


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


def test_forecast_endpoint_rejects_invalid_input():
    assert client.post("/api/forecast", json={"scenario": {}}).status_code == 422


def test_simulate_endpoint_accepts_valid_allocation_and_boundaries():
    scenario, forecast = _scenario_and_forecast()
    for allocation in (_allocation(teller=1, loans=1, customer_service=1), _allocation(teller=6, loans=3, customer_service=1)):
        response = client.post(
            "/api/simulate",
            json={"scenario": scenario, "forecast": forecast, "allocation": allocation},
        )
        assert response.status_code == 200
        assert set(response.json()["per_queue"]) == set(allocation["staff_by_queue"])


@pytest.mark.parametrize(
    ("allocation", "error"),
    [
        ({"label": "whatif", "staff_by_queue": {"teller": 3, "loans": 2, "customer_service": 2, "extra": 1}}, "allocation_queue_mismatch"),
        ({"label": "whatif", "staff_by_queue": {"teller": 3, "loans": 2}}, "allocation_queue_mismatch"),
        (_allocation(teller=0), "staff_limit_violation"),
        (_allocation(teller=7), "staff_limit_violation"),
        (_allocation(teller=-1), "staff_limit_violation"),
        (_allocation(teller=6, loans=3, customer_service=4), "staff_budget_exceeded"),
    ],
)
def test_simulate_endpoint_rejects_invalid_allocations(allocation, error):
    scenario, forecast = _scenario_and_forecast()
    response = client.post(
        "/api/simulate",
        json={"scenario": scenario, "forecast": forecast, "allocation": allocation},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == error


def test_simulate_negative_staff_uses_business_validation_error():
    scenario, forecast = _scenario_and_forecast()
    response = client.post(
        "/api/simulate",
        json={"scenario": scenario, "forecast": forecast, "allocation": _allocation(teller=-1)},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "error": "staff_limit_violation",
        "message": "Queue 'teller' staff must be between 1 and 6",
        "field": "allocation.staff_by_queue.teller",
    }


@pytest.mark.parametrize("mutation", ["scenario_name", "queue_ids", "slot_labels", "slot_length"])
def test_simulate_endpoint_rejects_incompatible_forecast(mutation):
    scenario, forecast = _scenario_and_forecast()
    bad_forecast = deepcopy(forecast)
    if mutation == "scenario_name":
        bad_forecast["scenario_name"] = "peak"
    elif mutation == "queue_ids":
        bad_forecast["expected_arrivals"]["extra"] = bad_forecast["expected_arrivals"].pop("teller")
    elif mutation == "slot_labels":
        bad_forecast["slots"][0] = "08:45"
    else:
        bad_forecast["slots"] = bad_forecast["slots"][:-1]

    response = client.post(
        "/api/simulate",
        json={"scenario": scenario, "forecast": bad_forecast, "allocation": _allocation()},
    )
    assert response.status_code == 422


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


def test_optimize_endpoint_is_deterministic_and_has_complete_contract():
    scenario, forecast = _scenario_and_forecast()
    request = {"scenario": scenario, "forecast": forecast}
    first = client.post("/api/optimize", json=request)
    second = client.post("/api/optimize", json=request)

    assert first.status_code == 200
    assert first.json() == second.json()
    assert {"scenario_name", "baseline", "optimized", "score_breakdown", "improvement", "explanation", "feasible"} <= set(first.json())


def test_optimize_endpoint_reports_infeasible_scenario():
    scenario, _ = _scenario_and_forecast()
    scenario["total_staff_available"] = 1
    forecast = client.post("/api/forecast", json={"scenario": scenario}).json()

    response = client.post("/api/optimize", json={"scenario": scenario, "forecast": forecast})

    assert response.status_code == 200
    assert response.json()["feasible"] is False


def test_optimize_endpoint_rejects_incompatible_forecast():
    scenario, forecast = _scenario_and_forecast()
    forecast["expected_arrivals"].pop("teller")
    response = client.post("/api/optimize", json={"scenario": scenario, "forecast": forecast})
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "forecast_queue_mismatch"


def test_explain_endpoint_is_deterministic():
    sc_resp = client.post("/api/scenario/generate", json={"scenario_name": "normal", "seed": 42})
    scenario = sc_resp.json()["scenario"]
    forecast = client.post("/api/forecast", json={"scenario": scenario}).json()
    optimization = client.post(
        "/api/optimize", json={"scenario": scenario, "forecast": forecast}
    ).json()
    request = {"scenario": scenario, "optimization": optimization}

    first = client.post("/api/explain", json=request)
    second = client.post("/api/explain", json=request)

    assert first.status_code == 200
    assert first.json() == second.json()
    assert set(first.json()) == {"explanation"}
    assert first.json()["explanation"] == optimization["explanation"]


def test_explain_endpoint_rejects_invalid_requests():
    assert client.post("/api/explain").status_code == 422
    assert client.post("/api/explain", json={"scenario": {}}).status_code == 422


def test_explain_endpoint_rejects_scenario_mismatch():
    scenario, forecast = _scenario_and_forecast()
    optimization = client.post(
        "/api/optimize", json={"scenario": scenario, "forecast": forecast}
    ).json()
    scenario["scenario_name"] = "peak"
    response = client.post("/api/explain", json={"scenario": scenario, "optimization": optimization})
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "scenario_mismatch"


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


def test_whatif_endpoint_rejects_invalid_allocation():
    scenario, forecast = _scenario_and_forecast()
    response = client.post(
        "/api/whatif",
        json={"scenario": scenario, "forecast": forecast, "allocation": _allocation(teller=7)},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "staff_limit_violation"


def test_whatif_negative_staff_uses_business_validation_error():
    scenario, forecast = _scenario_and_forecast()
    response = client.post(
        "/api/whatif",
        json={"scenario": scenario, "forecast": forecast, "allocation": _allocation(teller=-1)},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "error": "staff_limit_violation",
        "message": "Queue 'teller' staff must be between 1 and 6",
        "field": "allocation.staff_by_queue.teller",
    }


def test_whatif_endpoint_rejects_incompatible_forecast():
    scenario, forecast = _scenario_and_forecast()
    forecast["scenario_name"] = "peak"
    response = client.post(
        "/api/whatif",
        json={"scenario": scenario, "forecast": forecast, "allocation": _allocation()},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "scenario_mismatch"

def test_forecast_server_error_uses_safe_structured_response(monkeypatch):
    def fail_forecast(_scenario):
        raise RuntimeError("secret internal implementation detail")

    monkeypatch.setattr("backend.routes.forecast.forecast", fail_forecast)

    scenario = client.post(
        "/api/scenario/generate",
        json={"scenario_name": "normal", "seed": 42},
    ).json()["scenario"]

    response = client.post("/api/forecast", json={"scenario": scenario})

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "error": "forecast_error",
            "message": "Unable to generate forecast",
        }
    }
    assert "secret internal implementation detail" not in response.text

def test_global_server_error_uses_safe_structured_response(monkeypatch):
    @app.get("/api/test-internal-error")
    def test_internal_error():
        raise RuntimeError("secret global implementation detail")

    response = client.get("/api/test-internal-error")

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "error": "internal_server_error",
            "message": "An unexpected server error occurred",
        }
    }
    assert "secret global implementation detail" not in response.text


# ---------------------------------------------------------------------------
# KIRAN-003: API + Decision Pipeline Integration Hardening Tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("scenario_name", ["normal", "peak", "surge"])
def test_optimize_endpoint_executes_complete_pipeline_for_canonical_scenarios(scenario_name):
    """KIRAN-003: Verify /api/optimize supports canonical scenarios without requiring pre-computed forecast."""
    sc_resp = client.post("/api/scenario/generate", json={"scenario_name": scenario_name, "seed": 42})
    assert sc_resp.status_code == 200
    scenario = sc_resp.json()["scenario"]

    # Call /api/optimize with only scenario (pipeline auto-forecasts)
    resp = client.post("/api/optimize", json={"scenario": scenario})
    assert resp.status_code == 200
    data = resp.json()

    # Complete contract fields present
    assert data["feasible"] is True
    assert data["scenario_name"] == scenario_name
    assert "baseline" in data
    assert "optimized" in data
    assert "score_breakdown" in data
    assert "improvement" in data
    assert "explanation" in data
    assert "forecast" in data
    assert data["forecast"] is not None
    assert set(data["forecast"]["expected_arrivals"]) == set(q["queue_id"] for q in scenario["queues"])


def test_optimize_endpoint_accepts_and_validates_caller_forecast():
    """KIRAN-003: Verify /api/optimize still supports pre-computed forecasts."""
    scenario, forecast = _scenario_and_forecast()
    resp = client.post("/api/optimize", json={"scenario": scenario, "forecast": forecast})
    assert resp.status_code == 200
    data = resp.json()
    assert data["forecast"] == forecast


def test_optimize_endpoint_deterministic_repeatability():
    """KIRAN-003: Verify repeated requests with same seed produce identical responses."""
    sc_resp = client.post("/api/scenario/generate", json={"scenario_name": "surge", "seed": 42})
    scenario = sc_resp.json()["scenario"]

    first = client.post("/api/optimize", json={"scenario": scenario})
    second = client.post("/api/optimize", json={"scenario": scenario})

    assert first.status_code == 200
    assert first.json() == second.json()


def test_optimize_endpoint_exposes_baseline_vs_optimized_distinction():
    """KIRAN-003: Verify baseline and optimized allocations are distinct in surge scenario."""
    sc_resp = client.post("/api/scenario/generate", json={"scenario_name": "surge", "seed": 42})
    scenario = sc_resp.json()["scenario"]

    resp = client.post("/api/optimize", json={"scenario": scenario})
    assert resp.status_code == 200
    data = resp.json()

    base = data["baseline"]
    opt = data["optimized"]
    assert base["allocation"]["label"] == "baseline"
    assert opt["allocation"]["label"] == "optimized"
    assert base["result"]["allocation_label"] == "baseline"
    assert opt["result"]["allocation_label"] == "optimized"


def test_optimize_endpoint_safe_500_response(monkeypatch):
    """KIRAN-003: Verify internal exceptions do not leak stack traces or raw details."""
    def fail_pipeline(*args, **kwargs):
        raise RuntimeError("database connection failed with password xyz")

    monkeypatch.setattr("backend.routes.optimization.run_decision_pipeline", fail_pipeline)

    sc_resp = client.post("/api/scenario/generate", json={"scenario_name": "normal", "seed": 42})
    scenario = sc_resp.json()["scenario"]

    resp = client.post("/api/optimize", json={"scenario": scenario})
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": {
            "error": "optimize_error",
            "message": "Unable to compute optimization",
        }
    }
    assert "database connection failed" not in resp.text
    assert "password" not in resp.text


def test_optimize_endpoint_invalid_scenario_returns_422():
    """KIRAN-003: Verify malformed scenario returns structured 422 error."""
    resp = client.post("/api/optimize", json={"scenario": {"scenario_name": "invalid_name"}})
    assert resp.status_code == 422

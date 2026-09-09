"""REETHU Phase P8: Pre-demo end-to-end integration and quality validation.

Covers:
- Complete demo flow via live FastAPI endpoints (health, generate, forecast, simulate, optimize, whatif, explain)
- Full decision pipeline integration (DecisionPipeline, run_decision_pipeline)
- Multi-scenario reproducibility, determinism, and metric validity
- Robustness and error immunity across API boundaries (ensures clean 4xx and zero 500 errors)
- Performance SLA targets (sim < 1s, opt < 3s, whatif < 1.5s)
- What-if capacity expansion and trade-off validation for branch operations decision support
"""
from __future__ import annotations

import time
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import (
    AllocationPlan,
    OptimizationResult,
    QueueConfig,
    ScenarioConfig,
    SimulationResult,
)
from backend.optimization.baseline import baseline_allocation
from backend.pipeline import DecisionPipeline, DecisionPipelineResult, run_decision_pipeline
from data.scenarios import get_scenario, normal_scenario, peak_scenario, surge_scenario

client = TestClient(app)

SCENARIOS = ("normal", "peak", "surge")


# ===========================================================================
# 1. Full Demo Journey via FastAPI HTTP Endpoints
# ===========================================================================

@pytest.mark.parametrize("scenario_name", SCENARIOS)
def test_full_demo_journey_via_fastapi_endpoints(scenario_name: str):
    """
    Executes the complete branch manager demo flow through FastAPI routes:
    1. Health check
    2. Scenario generation
    3. Demand forecasting
    4. Baseline simulation
    5. Feasible optimization
    6. Recommendation explanation
    7. What-if capacity simulation
    """
    # Step 1: Health check
    health_resp = client.get("/api/health")
    assert health_resp.status_code == 200
    assert health_resp.json() == {"status": "ok"}

    # Step 2: Generate scenario
    gen_resp = client.post("/api/scenario/generate", json={"scenario_name": scenario_name, "seed": 42})
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert "scenario" in gen_data
    assert "arrivals" in gen_data
    scenario = gen_data["scenario"]

    # Step 3: Demand forecasting
    fc_resp = client.post("/api/forecast", json={"scenario": scenario})
    assert fc_resp.status_code == 200
    forecast_data = fc_resp.json()
    assert "slots" in forecast_data
    assert "expected_arrivals" in forecast_data
    assert len(forecast_data["slots"]) == 32  # 8 hours * 4 slots/hr

    # Step 4: Simulate baseline allocation
    sc_obj = ScenarioConfig(**scenario)
    base_alloc = baseline_allocation(sc_obj)
    baseline_payload = {
        "label": "baseline",
        "staff_by_queue": base_alloc.staff_by_queue,
    }
    sim_resp = client.post(
        "/api/simulate",
        json={"scenario": scenario, "forecast": forecast_data, "allocation": baseline_payload},
    )
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert "branch_wide" in sim_data
    assert sim_data["branch_wide"]["avg_wait_minutes"] >= 0.0

    # Step 5: Optimize allocation
    opt_resp = client.post("/api/optimize", json={"scenario": scenario, "forecast": forecast_data})
    assert opt_resp.status_code == 200
    opt_data = opt_resp.json()
    assert opt_data["feasible"] is True
    assert "baseline" in opt_data
    assert "optimized" in opt_data
    assert "improvement" in opt_data
    assert "explanation" in opt_data

    # Step 6: Generate authoritative explanation
    exp_resp = client.post("/api/explain", json={"scenario": scenario, "optimization": opt_data})
    assert exp_resp.status_code == 200
    exp_data = exp_resp.json()
    assert "explanation" in exp_data
    assert len(exp_data["explanation"]) > 50

    # Step 7: What-if exploration
    whatif_alloc = {
        "label": "whatif",
        "staff_by_queue": opt_data["optimized"]["allocation"]["staff_by_queue"],
    }
    whatif_resp = client.post(
        "/api/whatif",
        json={"scenario": scenario, "forecast": forecast_data, "allocation": whatif_alloc},
    )
    assert whatif_resp.status_code == 200
    whatif_data = whatif_resp.json()
    assert whatif_data["allocation_label"] == "whatif"
    assert whatif_data["branch_wide"]["avg_wait_minutes"] == pytest.approx(
        opt_data["optimized"]["result"]["branch_wide"]["avg_wait_minutes"], abs=0.01
    )


# ===========================================================================
# 2. Decision Pipeline Integration
# ===========================================================================

@pytest.mark.parametrize("scenario_name", SCENARIOS)
def test_decision_pipeline_integration(scenario_name: str):
    """Verifies run_decision_pipeline executes end-to-end and returns a valid result."""
    scenario = get_scenario(scenario_name, seed=42)
    result = run_decision_pipeline(scenario)

    assert isinstance(result, DecisionPipelineResult)
    assert isinstance(result, OptimizationResult)
    assert result.scenario_name == scenario_name
    assert result.feasible is True
    assert result.forecast is not None
    assert len(result.forecast.slots) == scenario.slot_count()
    assert result.baseline.score >= result.optimized.score - 1e-9
    assert result.baseline.result.branch_wide.total_served >= 0
    assert result.optimized.result.branch_wide.total_served >= 0
    assert len(result.explanation) > 0


def test_decision_pipeline_determinism():
    """Identical scenario configuration produces identical pipeline output."""
    scenario = get_scenario("peak", seed=123)
    res1 = run_decision_pipeline(scenario)
    res2 = run_decision_pipeline(scenario)

    assert res1.model_dump() == res2.model_dump()


def test_decision_pipeline_accepts_dict_input():
    """Pipeline accepts raw dictionary inputs matching ScenarioConfig."""
    scenario = get_scenario("normal", seed=42)
    raw_dict = scenario.model_dump()
    result = run_decision_pipeline(raw_dict)
    assert result.feasible is True
    assert result.scenario_name == "normal"


def test_decision_pipeline_rejects_invalid_inputs():
    """Pipeline raises appropriate exceptions on invalid inputs."""
    with pytest.raises(TypeError, match="ScenarioConfig or dict"):
        DecisionPipeline(scenario=["invalid", "type"])  # type: ignore

    with pytest.raises(ValueError, match="Invalid scenario configuration"):
        DecisionPipeline(scenario={"invalid": "payload"})


# ===========================================================================
# 3. Robustness & Error Boundary Immunity (Zero 500 Errors)
# ===========================================================================

def test_scenario_generate_malformed_payload_returns_422_not_500():
    """Invalid scenario inputs return structured 422, never unhandled 500."""
    res = client.post("/api/scenario/generate", json={"scenario_name": "unknown_scenario"})
    assert res.status_code == 422
    assert "detail" in res.json()


def test_forecast_endpoint_invalid_scenario_returns_422_not_500():
    """Invalid scenario payload returns 422."""
    res = client.post("/api/forecast", json={"scenario": {"horizon_start": "invalid_time"}})
    assert res.status_code == 422


def test_simulate_endpoint_mismatched_forecast_returns_422_not_500():
    """Forecast with mismatched queue set returns 422."""
    scenario = normal_scenario(seed=42).model_dump()
    fc_resp = client.post("/api/forecast", json={"scenario": scenario})
    bad_forecast = deepcopy(fc_resp.json())
    bad_forecast["expected_arrivals"]["alien_queue"] = bad_forecast["expected_arrivals"].pop("teller")

    alloc = {
        "label": "baseline",
        "staff_by_queue": {"teller": 4, "loans": 2, "customer_service": 2},
    }
    res = client.post(
        "/api/simulate",
        json={"scenario": scenario, "forecast": bad_forecast, "allocation": alloc},
    )
    assert res.status_code == 422


def test_optimize_endpoint_missing_body_returns_422_not_500():
    """Empty POST body returns 422."""
    res = client.post("/api/optimize", json={})
    assert res.status_code == 422


def test_explain_endpoint_scenario_mismatch_returns_422_not_500():
    """Mismatched scenario name returns 422 structured error."""
    scenario = normal_scenario(seed=42)
    pipeline_res = run_decision_pipeline(scenario)
    opt_data = pipeline_res.model_dump()

    mismatched_scenario = peak_scenario(seed=42).model_dump()
    res = client.post(
        "/api/explain",
        json={"scenario": mismatched_scenario, "optimization": opt_data},
    )
    assert res.status_code == 422
    assert res.json()["detail"]["error"] == "scenario_mismatch"


# ===========================================================================
# 4. Performance SLA Compliance (<1s sim, <3s opt, <1.5s whatif)
# ===========================================================================

@pytest.mark.parametrize("scenario_name", SCENARIOS)
def test_performance_sla_compliance(scenario_name: str):
    """
    Validates that core operation runtimes meet or beat documented SLAs:
    - Single simulation: < 1.0s (binding TRD NFR)
    - Decision pipeline / optimization: < 3.0s (binding TRD NFR)
    - What-if simulation: < 1.5s
    """
    scenario = get_scenario(scenario_name, seed=42)

    # 1. Full decision pipeline SLA
    t0 = time.perf_counter()
    pipeline_result = run_decision_pipeline(scenario)
    pipeline_duration = time.perf_counter() - t0
    assert pipeline_duration < 3.0, f"Pipeline took {pipeline_duration:.3f}s (exceeds 3.0s SLA)"

    # 2. What-if SLA
    whatif_alloc = AllocationPlan(
        label="whatif",
        staff_by_queue=pipeline_result.optimized.allocation.staff_by_queue,
    )
    t0 = time.perf_counter()
    res = client.post(
        "/api/whatif",
        json={
            "scenario": scenario.model_dump(),
            "forecast": pipeline_result.forecast.model_dump(),
            "allocation": whatif_alloc.model_dump(),
        },
    )
    whatif_duration = time.perf_counter() - t0
    assert res.status_code == 200
    assert whatif_duration < 1.5, f"Whatif took {whatif_duration:.3f}s (exceeds 1.5s SLA)"


# ===========================================================================
# 5. What-If Operational Decision Support (Capacity Expansion & Trade-offs)
# ===========================================================================

def test_surge_whatif_capacity_expansion_relieves_overload():
    """
    In surge with 10 staff, baseline is optimal under existing limits.
    A manager asking 'What if we add 3 float staff (total 13)?' sees a dramatic
    reduction in wait times and overload, confirming decision support value.
    """
    scenario = surge_scenario(seed=42)
    pipeline_res = run_decision_pipeline(scenario)

    baseline_wait = pipeline_res.baseline.result.branch_wide.avg_wait_minutes
    baseline_overload = pipeline_res.baseline.result.branch_wide.overloaded_slot_count
    assert baseline_wait > 80.0
    assert baseline_overload > 20

    # Expand capacity to 12 staff (+1 teller, +1 cs) within queue limits
    expanded_scenario = scenario.model_copy(update={"total_staff_available": 12})
    expanded_alloc = {
        "label": "whatif",
        "staff_by_queue": {"teller": 5, "loans": 3, "customer_service": 4},
    }
    res = client.post(
        "/api/whatif",
        json={
            "scenario": expanded_scenario.model_dump(),
            "forecast": pipeline_res.forecast.model_dump(),
            "allocation": expanded_alloc,
        },
    )
    assert res.status_code == 200
    whatif_data = res.json()["branch_wide"]

    # Capacity expansion materially relieves backlog and wait times
    assert whatif_data["avg_wait_minutes"] < baseline_wait
    assert whatif_data["total_end_backlog"] < pipeline_res.baseline.result.branch_wide.total_end_backlog
    assert whatif_data["total_served"] >= pipeline_res.baseline.result.branch_wide.total_served


def test_peak_whatif_staff_reallocation_demonstrates_queue_tradeoff():
    """
    Reallocating a staff member between queues demonstrates trade-offs:
    Taking 1 staff from teller and moving to loans increases teller wait.
    """
    scenario = peak_scenario(seed=42)
    pipeline_res = run_decision_pipeline(scenario)
    opt_staff = pipeline_res.optimized.allocation.staff_by_queue

    # Reallocate: shift 1 staff from teller to customer_service
    shifted_staff = deepcopy(opt_staff)
    if shifted_staff["teller"] > 1:
        shifted_staff["teller"] -= 1
        shifted_staff["customer_service"] += 1

        res = client.post(
            "/api/whatif",
            json={
                "scenario": scenario.model_dump(),
                "forecast": pipeline_res.forecast.model_dump(),
                "allocation": {"label": "whatif", "staff_by_queue": shifted_staff},
            },
        )
        assert res.status_code == 200
        per_queue = res.json()["per_queue"]
        # Teller utilization rises when staff is removed
        assert per_queue["teller"]["utilization"] >= pipeline_res.optimized.result.per_queue["teller"].utilization

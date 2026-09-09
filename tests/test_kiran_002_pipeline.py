"""
tests/test_kiran_002_pipeline.py — Focused integration tests for KIRAN-002.

Validates the end-to-end deterministic decision pipeline:
  - Normal, peak, surge scenario execution
  - Output contract compatibility with OptimizationResult and api-contract.md
  - Separate simulation runs for baseline and optimized allocations
  - Deterministic repeatability and multi-seed robustness
  - Dict scenario input and pre-computed forecast support
  - Infeasible scenario and invalid input rejection
  - Sub-3-second execution performance target
"""

from __future__ import annotations

import time
import pytest

from backend.models import (
    AllocationPlan,
    ForecastResult,
    OptimizationResult,
    QueueConfig,
    ScenarioConfig,
)
from backend.pipeline import DecisionPipeline, DecisionPipelineResult, run_decision_pipeline
from backend.simulation.engine import simulate
from data.generator import generate_slot_labels
from data.scenarios import get_scenario, normal_scenario, peak_scenario, surge_scenario

SEED = 42


# ---------------------------------------------------------------------------
# 1. Normal scenario complete flow and contract shape
# ---------------------------------------------------------------------------
def test_pipeline_normal_scenario():
    """Verify complete decision pipeline execution for normal scenario."""
    scenario = normal_scenario(seed=SEED)
    result = run_decision_pipeline(scenario)

    assert isinstance(result, OptimizationResult)
    assert isinstance(result, DecisionPipelineResult)
    assert result.feasible is True
    assert result.scenario_name == "normal"

    # Baseline & optimized allocations
    base_alloc = result.baseline.allocation
    opt_alloc = result.optimized.allocation
    assert base_alloc.label == "baseline"
    assert opt_alloc.label == "optimized"
    assert base_alloc.total_staff() <= scenario.total_staff_available
    assert opt_alloc.total_staff() <= scenario.total_staff_available

    # Real simulation metrics present
    assert set(result.baseline.result.per_queue) == {"teller", "loans", "customer_service"}
    assert set(result.optimized.result.per_queue) == {"teller", "loans", "customer_service"}
    assert result.baseline.result.branch_wide.total_served > 0
    assert result.optimized.result.branch_wide.total_served > 0

    # Attached forecast
    assert result.forecast is not None
    assert result.forecast.scenario_name == "normal"
    assert len(result.forecast.slots) == scenario.slot_count()

    # Score breakdown & explanation
    assert result.score_breakdown.total_score >= 0.0
    assert "Scenario: NORMAL" in result.explanation
    assert "Hard constraints respected" in result.explanation


# ---------------------------------------------------------------------------
# 2. Peak scenario complete flow
# ---------------------------------------------------------------------------
def test_pipeline_peak_scenario():
    """Verify complete decision pipeline execution for peak scenario."""
    scenario = peak_scenario(seed=SEED)
    result = run_decision_pipeline(scenario)

    assert result.feasible is True
    assert result.scenario_name == "peak"
    assert result.optimized.score <= result.baseline.score + 1e-9

    for q in scenario.queues:
        staff = result.optimized.allocation.staff_by_queue[q.queue_id]
        assert q.min_staff <= staff <= q.max_staff


# ---------------------------------------------------------------------------
# 3. Surge scenario complete flow & overload detection
# ---------------------------------------------------------------------------
def test_pipeline_surge_scenario():
    """Verify complete decision pipeline execution for surge scenario."""
    scenario = surge_scenario(seed=SEED)
    result = run_decision_pipeline(scenario)

    assert result.feasible is True
    assert result.scenario_name == "surge"

    # Surge induces overload under baseline
    assert result.baseline.result.branch_wide.overloaded_slot_count > 0

    # Optimized allocation must not worsen p95 or overloaded slots
    base_bw = result.baseline.result.branch_wide
    opt_bw = result.optimized.result.branch_wide
    assert opt_bw.p95_wait_minutes <= base_bw.p95_wait_minutes * 1.05
    assert opt_bw.overloaded_slot_count <= base_bw.overloaded_slot_count

    # Explanation contains trace of computed metrics
    assert "Surge" in result.explanation or "SURGE" in result.explanation
    assert "Overload detected" in result.explanation or "Baseline allocation" in result.explanation


# ---------------------------------------------------------------------------
# 4. Verification that baseline and optimized are genuine separate simulations
# ---------------------------------------------------------------------------
def test_pipeline_baseline_and_optimized_are_separate_simulations():
    """Verify baseline and optimized simulation results come from distinct simulation executions."""
    scenario = surge_scenario(seed=SEED)
    result = run_decision_pipeline(scenario)

    # Distinct object identities
    assert result.baseline.result is not result.optimized.result
    assert result.baseline.result.allocation_label == "baseline"
    assert result.optimized.result.allocation_label == "optimized"

    # Re-run simulation directly with the same inputs to verify simulator was invoked faithfully
    avg_service_times = {q.queue_id: q.avg_service_time_minutes for q in scenario.queues}
    independent_baseline_sim = simulate(
        result.forecast,
        result.baseline.allocation,
        avg_service_times,
        scenario.slot_minutes,
    )
    independent_opt_sim = simulate(
        result.forecast,
        result.optimized.allocation,
        avg_service_times,
        scenario.slot_minutes,
    )

    assert result.baseline.result.branch_wide.avg_wait_minutes == pytest.approx(
        independent_baseline_sim.branch_wide.avg_wait_minutes
    )
    assert result.optimized.result.branch_wide.avg_wait_minutes == pytest.approx(
        independent_opt_sim.branch_wide.avg_wait_minutes
    )


# ---------------------------------------------------------------------------
# 5. Deterministic repeatability across identical runs
# ---------------------------------------------------------------------------
def test_pipeline_deterministic_repeatability():
    """Verify identical inputs produce identical allocations, scores, and explanations."""
    scenario_a = surge_scenario(seed=SEED)
    scenario_b = surge_scenario(seed=SEED)

    run_a = run_decision_pipeline(scenario_a)
    run_b = run_decision_pipeline(scenario_b)

    assert run_a.optimized.allocation.staff_by_queue == run_b.optimized.allocation.staff_by_queue
    assert run_a.optimized.score == pytest.approx(run_b.optimized.score)
    assert run_a.baseline.score == pytest.approx(run_b.baseline.score)
    assert run_a.explanation == run_b.explanation
    assert run_a.improvement == run_b.improvement


# ---------------------------------------------------------------------------
# 6. Multi-seed robustness
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("seed", [1, 7, 42, 99, 123])
def test_pipeline_multi_seed_robustness(seed):
    """Verify pipeline functions robustly across diverse random seeds."""
    scenario = get_scenario("peak", seed=seed)
    result = run_decision_pipeline(scenario)

    assert result.feasible is True
    total_staff = result.optimized.allocation.total_staff()
    assert total_staff <= scenario.total_staff_available
    for q in scenario.queues:
        s = result.optimized.allocation.staff_by_queue[q.queue_id]
        assert q.min_staff <= s <= q.max_staff


# ---------------------------------------------------------------------------
# 7. Accepts dictionary scenario input
# ---------------------------------------------------------------------------
def test_pipeline_accepts_dict_input():
    """Verify pipeline accepts raw dictionary input matching ScenarioConfig."""
    scenario = normal_scenario(seed=SEED)
    scenario_dict = scenario.model_dump()

    result = run_decision_pipeline(scenario_dict)
    assert result.feasible is True
    assert result.scenario_name == "normal"
    assert isinstance(result, DecisionPipelineResult)


# ---------------------------------------------------------------------------
# 8. Accepts custom pre-computed forecast
# ---------------------------------------------------------------------------
def test_pipeline_accepts_custom_forecast():
    """Verify pipeline uses a supplied ForecastResult without regenerating."""
    scenario = normal_scenario(seed=SEED)
    slots = generate_slot_labels(scenario)
    custom_forecast = ForecastResult(
        scenario_name="normal",
        slots=slots,
        expected_arrivals={
            "teller": [3.0] * len(slots),
            "loans": [1.0] * len(slots),
            "customer_service": [2.0] * len(slots),
        },
    )

    result = run_decision_pipeline(scenario, forecast_result=custom_forecast)
    assert result.feasible is True
    assert result.forecast.expected_arrivals["teller"] == [3.0] * len(slots)


# ---------------------------------------------------------------------------
# 9. Invalid inputs rejected
# ---------------------------------------------------------------------------
def test_pipeline_invalid_inputs_rejected():
    """Verify invalid scenario inputs raise ValueError or TypeError."""
    # Invalid type
    with pytest.raises(TypeError):
        run_decision_pipeline(12345)

    # Invalid dictionary structure
    with pytest.raises(ValueError):
        run_decision_pipeline({"scenario_name": "unknown_scenario"})

    # Mismatched forecast scenario name
    scenario = normal_scenario(seed=SEED)
    wrong_forecast = ForecastResult(
        scenario_name="surge",
        slots=generate_slot_labels(scenario),
        expected_arrivals={
            "teller": [1.0] * 32,
            "loans": [1.0] * 32,
            "customer_service": [1.0] * 32,
        },
    )
    with pytest.raises(ValueError, match="forecast.scenario_name must match scenario.scenario_name"):
        run_decision_pipeline(scenario, forecast_result=wrong_forecast)


# ---------------------------------------------------------------------------
# 10. Infeasible scenario handled gracefully (FR-OPT-5)
# ---------------------------------------------------------------------------
def test_pipeline_infeasible_scenario_handled():
    """Verify scenario where sum(min_staff) > total_staff_available returns feasible=False."""
    infeasible_scenario = ScenarioConfig(
        scenario_name="normal",
        seed=SEED,
        horizon_start="09:00",
        horizon_end="17:00",
        slot_minutes=15,
        queues=[
            QueueConfig(queue_id="q1", name="Queue 1", min_staff=5, max_staff=10, avg_service_time_minutes=5.0),
            QueueConfig(queue_id="q2", name="Queue 2", min_staff=5, max_staff=10, avg_service_time_minutes=5.0),
        ],
        total_staff_available=8,  # sum(min_staff)=10 > 8
    )

    result = run_decision_pipeline(infeasible_scenario)
    assert result.feasible is False
    assert "No feasible allocation" in result.explanation
    assert result.optimized.allocation == result.baseline.allocation


# ---------------------------------------------------------------------------
# 11. Performance target (sub-3-second execution)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("scenario_func", [normal_scenario, peak_scenario, surge_scenario])
def test_pipeline_performance_sub_three_seconds(scenario_func):
    """Verify end-to-end pipeline execution time is well under the 3.0s requirement."""
    scenario = scenario_func(seed=SEED)
    t0 = time.perf_counter()
    result = run_decision_pipeline(scenario)
    elapsed = time.perf_counter() - t0

    assert result.feasible is True
    assert elapsed < 3.0, f"Pipeline execution took {elapsed:.3f}s (target: < 3.0s)"

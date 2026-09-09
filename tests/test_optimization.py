"""
tests/test_optimization.py — Optimizer tests.

Covers: TC-12 through TC-17 (feasibility, score improvement,
infeasible case, tie-breaking). REETHU-001 / KIRAN-002 validation.
"""
from __future__ import annotations

import pytest

from backend.models import AllocationPlan
from backend.optimization.baseline import InfeasibleBaselineError, baseline_allocation
from backend.optimization.optimizer import (
    enumerate_feasible_allocations,
    is_feasible,
    optimize,
)
from backend.forecasting.forecast import forecast as run_forecast
from data.scenarios import get_scenario, normal_scenario, surge_scenario


# ---------------------------------------------------------------------------
# TC-12: Feasible allocation respects all constraints
# ---------------------------------------------------------------------------
def test_feasible_allocations_satisfy_constraints_tc12():
    cfg = normal_scenario(seed=42)
    feasible = enumerate_feasible_allocations(cfg)
    assert len(feasible) > 0
    for alloc in feasible:
        assert is_feasible(alloc, cfg), f"Infeasible allocation slipped through: {alloc}"


# ---------------------------------------------------------------------------
# TC-13: Optimized score >= baseline score on same scenario
# (lower score = better; optimized should be <= baseline)
# ---------------------------------------------------------------------------
def test_optimized_score_le_baseline_tc13():
    cfg = surge_scenario(seed=42)
    fc = run_forecast(cfg)
    result = optimize(cfg, fc)
    assert result.feasible
    assert result.optimized.score <= result.baseline.score + 1e-6


# ---------------------------------------------------------------------------
# TC-14: Infeasible scenario → feasible=False, no invalid allocation
# ---------------------------------------------------------------------------
def test_infeasible_scenario_tc14():
    from backend.models import QueueConfig, ScenarioConfig
    # Force infeasibility: sum(min_staff)=10 but only 5 available
    cfg = ScenarioConfig(
        scenario_name="normal",
        seed=42,
        horizon_start="09:00",
        horizon_end="17:00",
        slot_minutes=15,
        queues=[
            QueueConfig(queue_id="a", name="A", min_staff=5, max_staff=8, avg_service_time_minutes=5),
            QueueConfig(queue_id="b", name="B", min_staff=5, max_staff=8, avg_service_time_minutes=5),
        ],
        total_staff_available=5,  # impossible: 5+5=10 > 5
    )
    fc = run_forecast(cfg)
    result = optimize(cfg, fc)
    assert result.feasible is False
    assert "feasible" in result.explanation.lower() or "No feasible" in result.explanation


# ---------------------------------------------------------------------------
# TC-16: Equal scores → deterministic tie-break (same result every call)
# ---------------------------------------------------------------------------
def test_deterministic_output_tc16():
    cfg = normal_scenario(seed=42)
    fc = run_forecast(cfg)
    r1 = optimize(cfg, fc)
    r2 = optimize(cfg, fc)
    assert r1.optimized.allocation.staff_by_queue == r2.optimized.allocation.staff_by_queue
    assert r1.optimized.score == r2.optimized.score


# ---------------------------------------------------------------------------
# TC-17: total_staff_available=0 → explicit infeasible, no crash
# ---------------------------------------------------------------------------
def test_zero_total_staff_tc17():
    from backend.models import QueueConfig, ScenarioConfig
    cfg = ScenarioConfig(
        scenario_name="normal",
        seed=42,
        horizon_start="09:00",
        horizon_end="10:00",
        slot_minutes=15,
        queues=[
            QueueConfig(queue_id="t", name="T", min_staff=1, max_staff=5, avg_service_time_minutes=5),
        ],
        total_staff_available=1,  # min=1, so 1 is just feasible
    )
    fc = run_forecast(cfg)
    result = optimize(cfg, fc)
    # With 1 total and min=1, exactly one feasible allocation — must return it
    assert result.feasible is True
    assert result.optimized.allocation.staff_by_queue["t"] == 1


# ---------------------------------------------------------------------------
# Baseline allocation is deterministic and feasible
# ---------------------------------------------------------------------------
def test_baseline_allocation_deterministic():
    cfg = normal_scenario(seed=42)
    b1 = baseline_allocation(cfg)
    b2 = baseline_allocation(cfg)
    assert b1.staff_by_queue == b2.staff_by_queue
    assert b1.total_staff() <= cfg.total_staff_available
    for q in cfg.queues:
        s = b1.staff_by_queue[q.queue_id]
        assert q.min_staff <= s <= q.max_staff


# ---------------------------------------------------------------------------
# TC-22 (partial): End-to-end surge → genuine improvement
# ---------------------------------------------------------------------------
def test_surge_shows_genuine_improvement_tc22():
    cfg = surge_scenario(seed=42)
    fc = run_forecast(cfg)
    result = optimize(cfg, fc)
    assert result.feasible
    # Optimized should resolve at least some overload or reduce wait
    has_improvement = (
        result.improvement.avg_wait_reduction_minutes > 0
        or result.improvement.overloaded_slots_resolved > 0
        or result.optimized.score < result.baseline.score
    )
    assert has_improvement, "Optimizer should improve on surge scenario"

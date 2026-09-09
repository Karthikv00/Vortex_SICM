"""
tests/test_simulation.py — Simulation engine tests.

Covers: TC-04 through TC-09 (normal/peak/surge, zero arrivals,
zero staff, excess staff). REETHU-001 / KARTHI-003 validation.
"""
from __future__ import annotations

import pytest

from backend.models import AllocationPlan, ForecastResult
from backend.simulation.engine import simulate
from data.scenarios import normal_scenario, peak_scenario, surge_scenario
from backend.forecasting.forecast import forecast as run_forecast


def _make_forecast(arrivals_per_queue: dict[str, list[float]], slots: list[str]) -> ForecastResult:
    return ForecastResult(
        scenario_name="test",
        slots=slots,
        expected_arrivals=arrivals_per_queue,
    )


def _slots(n=4):
    return [f"09:{i*15:02d}" for i in range(n)]


# ---------------------------------------------------------------------------
# TC-04: Normal + adequate staff → low/no overload
# ---------------------------------------------------------------------------
def test_normal_adequate_staff_low_overload_tc04():
    cfg = normal_scenario(seed=42)
    fc = run_forecast(cfg)
    allocation = AllocationPlan(
        label="baseline",
        staff_by_queue={"teller": 5, "loans": 2, "customer_service": 3},
    )
    avg_times = {q.queue_id: q.avg_service_time_minutes for q in cfg.queues}
    result = simulate(fc, allocation, avg_times, cfg.slot_minutes)
    assert result.branch_wide.avg_wait_minutes >= 0
    # With adequate staff, avg wait should be modest (< 20 min)
    assert result.branch_wide.avg_wait_minutes < 20.0


# ---------------------------------------------------------------------------
# TC-07: Zero arrivals → zero wait, zero utilization, no crash
# ---------------------------------------------------------------------------
def test_zero_arrivals_tc07():
    slots = _slots(4)
    fc = _make_forecast({"q1": [0.0, 0.0, 0.0, 0.0]}, slots)
    alloc = AllocationPlan(label="baseline", staff_by_queue={"q1": 3})
    avg_times = {"q1": 5.0}
    result = simulate(fc, alloc, avg_times, 15)
    assert result.branch_wide.avg_wait_minutes == 0.0
    assert result.branch_wide.p95_wait_minutes == 0.0
    assert result.branch_wide.overloaded_slot_count == 0
    assert result.per_queue["q1"].total_served == 0


# ---------------------------------------------------------------------------
# TC-08: Zero staff + arrivals → overloaded, backlog grows, no crash
# ---------------------------------------------------------------------------
def test_zero_staff_with_arrivals_tc08():
    slots = _slots(4)
    fc = _make_forecast({"q1": [5.0, 5.0, 5.0, 5.0]}, slots)
    alloc = AllocationPlan(label="baseline", staff_by_queue={"q1": 0})
    avg_times = {"q1": 5.0}
    result = simulate(fc, alloc, avg_times, 15)
    qr = result.per_queue["q1"]
    assert qr.total_served == 0
    assert qr.end_backlog > 0
    assert len(qr.overloaded_slots) > 0


# ---------------------------------------------------------------------------
# TC-09: Staff far above demand → near-zero utilization, no divide-by-zero
# ---------------------------------------------------------------------------
def test_excess_staff_no_crash_tc09():
    slots = _slots(4)
    fc = _make_forecast({"q1": [1.0, 1.0, 1.0, 1.0]}, slots)
    alloc = AllocationPlan(label="whatif", staff_by_queue={"q1": 50})
    avg_times = {"q1": 5.0}
    result = simulate(fc, alloc, avg_times, 15)
    qr = result.per_queue["q1"]
    assert qr.utilization >= 0.0
    assert qr.avg_wait_minutes >= 0.0
    assert qr.end_backlog == 0
    assert result.branch_wide.overloaded_slot_count == 0


# ---------------------------------------------------------------------------
# TC-05: Peak + baseline staff → some overload expected
# ---------------------------------------------------------------------------
def test_peak_shows_more_overload_than_normal():
    norm_cfg = normal_scenario(seed=42)
    peak_cfg = peak_scenario(seed=42)
    avg_times = {q.queue_id: q.avg_service_time_minutes for q in norm_cfg.queues}
    # Tight allocation: minimums only
    tight = AllocationPlan(
        label="baseline",
        staff_by_queue={q.queue_id: q.min_staff for q in norm_cfg.queues},
    )
    norm_result = simulate(run_forecast(norm_cfg), tight, avg_times, norm_cfg.slot_minutes)
    peak_result = simulate(run_forecast(peak_cfg), tight, avg_times, peak_cfg.slot_minutes)
    # Peak should have >= overloaded slots as normal
    assert peak_result.branch_wide.avg_wait_minutes >= norm_result.branch_wide.avg_wait_minutes


# ---------------------------------------------------------------------------
# TC-06: Surge + baseline staff → significant overload
# ---------------------------------------------------------------------------
def test_surge_significant_overload_tc06():
    cfg = surge_scenario(seed=42)
    fc = run_forecast(cfg)
    avg_times = {q.queue_id: q.avg_service_time_minutes for q in cfg.queues}
    tight = AllocationPlan(
        label="baseline",
        staff_by_queue={q.queue_id: q.min_staff for q in cfg.queues},
    )
    result = simulate(fc, tight, avg_times, cfg.slot_minutes)
    # Surge with minimum staff must show meaningful overload
    assert result.branch_wide.overloaded_slot_count > 0
    assert result.branch_wide.avg_wait_minutes > 0


# ---------------------------------------------------------------------------
# Simulation result shape validity
# ---------------------------------------------------------------------------
def test_simulation_result_has_all_queues():
    cfg = normal_scenario(seed=42)
    fc = run_forecast(cfg)
    avg_times = {q.queue_id: q.avg_service_time_minutes for q in cfg.queues}
    alloc = AllocationPlan(
        label="baseline",
        staff_by_queue={q.queue_id: q.min_staff for q in cfg.queues},
    )
    result = simulate(fc, alloc, avg_times, cfg.slot_minutes)
    for q in cfg.queues:
        assert q.queue_id in result.per_queue


# ---------------------------------------------------------------------------
# Missing queue in allocation raises ValueError
# ---------------------------------------------------------------------------
def test_missing_queue_in_allocation_raises():
    slots = _slots(2)
    fc = _make_forecast({"q1": [2.0, 2.0], "q2": [1.0, 1.0]}, slots)
    alloc = AllocationPlan(label="baseline", staff_by_queue={"q1": 2})  # q2 missing
    with pytest.raises(ValueError, match="q2"):
        simulate(fc, alloc, {"q1": 5.0, "q2": 5.0}, 15)

# Zero staff + any positive backlog must be overloaded from first slot
def test_zero_staff_any_backlog_is_overloaded():
    slots = _slots(2)
    fc = _make_forecast({"q1": [1.0, 0.0]}, slots)
    alloc = AllocationPlan(label="baseline", staff_by_queue={"q1": 0})
    result = simulate(fc, alloc, {"q1": 5.0}, 15)

    assert result.per_queue["q1"].overloaded_slots == slots


def test_invalid_slot_minutes_rejected():
    slots = _slots(2)
    fc = _make_forecast({"q1": [1.0, 1.0]}, slots)
    alloc = AllocationPlan(label="baseline", staff_by_queue={"q1": 2})

    with pytest.raises(ValueError, match="slot_minutes"):
        simulate(fc, alloc, {"q1": 5.0}, 0)


def test_negative_arrivals_rejected():
    """Negative arrivals are rejected at the ForecastResult model level (KARTHI-002)."""
    slots = _slots(2)
    from pydantic import ValidationError
    with pytest.raises(ValidationError, match="negative"):
        _make_forecast({"q1": [-1.0, 2.0]}, slots)

"""REETHU-002: Simulation edge-case and invariant validation.

Covers time-step queue simulation invariants, constraint boundaries,
and error handling without modifying production behavior.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.models import AllocationPlan, ForecastResult, SimulationResult
from backend.simulation.engine import simulate


def _forecast_for(arrivals: dict[str, list[float]], slot_minutes: int = 15) -> ForecastResult:
    n = len(next(iter(arrivals.values())))
    slots = [f"{9 + (i * slot_minutes) // 60:02d}:{(i * slot_minutes) % 60:02d}" for i in range(n)]
    return ForecastResult(scenario_name="normal", slots=slots, expected_arrivals=arrivals)


def _allocation(staff: dict[str, int], label: str = "baseline") -> AllocationPlan:
    return AllocationPlan(label=label, staff_by_queue=staff)


def test_negative_staff_rejected_by_allocation_plan():
    """AllocationPlan rejects negative staff count via model validation."""
    with pytest.raises(ValidationError, match="cannot be negative"):
        AllocationPlan(label="baseline", staff_by_queue={"teller": -1})


def test_negative_staff_rejected_by_simulation_engine():
    """simulate() defensively rejects negative staff even if model validation is bypassed."""
    bad_plan = AllocationPlan.model_construct(label="baseline", staff_by_queue={"teller": -1})
    forecast = _forecast_for({"teller": [2.0, 2.0]})
    with pytest.raises(ValueError, match="cannot be negative"):
        simulate(forecast, bad_plan, {"teller": 4.0})


def test_missing_service_time_rejected():
    """simulate() raises ValueError when a forecast queue is missing from avg_service_times."""
    forecast = _forecast_for({"teller": [1.0]})
    plan = _allocation({"teller": 1})
    with pytest.raises(ValueError, match="avg_service_times"):
        simulate(forecast, plan, {})


def test_zero_service_time_rejected():
    """simulate() raises ValueError when avg_service_time is zero."""
    forecast = _forecast_for({"teller": [1.0]})
    plan = _allocation({"teller": 1})
    with pytest.raises(ValueError, match="must be > 0"):
        simulate(forecast, plan, {"teller": 0.0})


def test_negative_service_time_rejected():
    """simulate() raises ValueError when avg_service_time is negative."""
    forecast = _forecast_for({"teller": [1.0]})
    plan = _allocation({"teller": 1})
    with pytest.raises(ValueError, match="must be > 0"):
        simulate(forecast, plan, {"teller": -3.5})


def test_invalid_slot_minutes_rejected():
    """simulate() raises ValueError when slot_minutes <= 0."""
    forecast = _forecast_for({"teller": [1.0]})
    plan = _allocation({"teller": 1})
    with pytest.raises(ValueError, match="slot_minutes must be > 0"):
        simulate(forecast, plan, {"teller": 4.0}, slot_minutes=0)
    with pytest.raises(ValueError, match="slot_minutes must be > 0"):
        simulate(forecast, plan, {"teller": 4.0}, slot_minutes=-15)


def test_allocation_missing_queue_raises():
    """simulate() raises ValueError when allocation is missing a forecast queue."""
    forecast = _forecast_for({"teller": [2.0], "loans": [1.0]})
    plan = _allocation({"teller": 2})  # "loans" missing
    with pytest.raises(ValueError, match="loans"):
        simulate(forecast, plan, {"teller": 4.0, "loans": 15.0})


def test_zero_staff_backlog_grows_and_equals_total_arrivals():
    """With zero staff, nobody is served, backlog equals arrival sum, and overload is flagged."""
    forecast = _forecast_for({"teller": [1.0, 2.0, 3.0]})
    result = simulate(forecast, _allocation({"teller": 0}), {"teller": 4.0})
    queue = result.per_queue["teller"]
    assert queue.total_served == 0
    assert queue.end_backlog == 6
    assert len(queue.overloaded_slots) == 3


def test_zero_staff_any_backlog_is_overloaded():
    """With zero staff, any slot with backlog > 0 is flagged as overloaded."""
    forecast = _forecast_for({"teller": [5.0, 0.0, 0.0]})
    result = simulate(forecast, _allocation({"teller": 0}), {"teller": 4.0})
    queue = result.per_queue["teller"]
    assert queue.overloaded_slots == forecast.slots


def test_overload_labels_are_subset_of_forecast_slots():
    """Overloaded slot labels reported must strictly be a subset of the forecast slots."""
    forecast = _forecast_for({"teller": [10.0, 10.0]})
    result = simulate(forecast, _allocation({"teller": 0}), {"teller": 4.0})
    assert set(result.per_queue["teller"].overloaded_slots).issubset(set(forecast.slots))


def test_branch_overload_count_is_unique_slot_union():
    """Branch-wide overloaded_slot_count counts the union of overloaded slots across queues."""
    forecast = ForecastResult(
        scenario_name="normal",
        slots=["09:00"],
        expected_arrivals={"teller": [10.0], "loans": [10.0]},
    )
    result = simulate(
        forecast,
        _allocation({"teller": 0, "loans": 0}),
        {"teller": 4.0, "loans": 15.0},
    )
    assert result.per_queue["teller"].overloaded_slots == ["09:00"]
    assert result.per_queue["loans"].overloaded_slots == ["09:00"]
    assert result.branch_wide.overloaded_slot_count == 1


def test_p95_wait_is_at_least_average_wait():
    """p95 wait must be greater than or equal to average wait for both queue and branch."""
    forecast = _forecast_for({"teller": [1.0, 8.0, 8.0, 2.0]})
    result = simulate(forecast, _allocation({"teller": 1}), {"teller": 4.0})
    queue = result.per_queue["teller"]
    assert queue.p95_wait_minutes >= queue.avg_wait_minutes >= 0.0
    assert result.branch_wide.p95_wait_minutes >= result.branch_wide.avg_wait_minutes >= 0.0


def test_utilization_bounded_between_zero_and_one():
    """Utilization is always within [0.0, 1.0], even under massive customer surge."""
    forecast = _forecast_for({"teller": [500.0]})
    result = simulate(forecast, _allocation({"teller": 1}), {"teller": 1.0})
    assert 0.0 <= result.per_queue["teller"].utilization <= 1.0


def test_simulation_is_deterministic():
    """Running simulation twice with identical inputs yields identical results."""
    forecast = _forecast_for({"teller": [2.0, 5.0, 1.0], "loans": [1.0, 2.0, 3.0]})
    plan = _allocation({"teller": 2, "loans": 1})
    services = {"teller": 4.0, "loans": 15.0}
    r1 = simulate(forecast, plan, services)
    r2 = simulate(forecast, plan, services)
    assert r1 == r2


def test_single_slot_horizon_is_supported():
    """A single-slot horizon runs cleanly and computes non-negative results."""
    forecast = _forecast_for({"teller": [2.0]})
    result = simulate(forecast, _allocation({"teller": 1}), {"teller": 4.0})
    assert result.per_queue["teller"].total_served >= 0
    assert result.per_queue["teller"].end_backlog >= 0
    assert result.branch_wide.avg_wait_minutes >= 0.0


def test_zero_arrivals_produces_all_zero_metrics():
    """Zero arrivals across all slots produces zero waits, zero utilization, and no overloads."""
    forecast = _forecast_for({"teller": [0.0, 0.0, 0.0]})
    result = simulate(forecast, _allocation({"teller": 2}), {"teller": 4.0})
    queue = result.per_queue["teller"]
    assert queue.avg_wait_minutes == 0.0
    assert queue.p95_wait_minutes == 0.0
    assert queue.utilization == 0.0
    assert queue.overloaded_slots == []
    assert queue.total_served == 0
    assert queue.end_backlog == 0
    assert result.branch_wide.avg_wait_minutes == 0.0
    assert result.branch_wide.overloaded_slot_count == 0


def test_massively_oversupplied_staff_utilization_near_zero():
    """Staff far exceeding demand results in near-zero utilization and zero backlog."""
    forecast = _forecast_for({"teller": [1.0, 1.0]})
    result = simulate(forecast, _allocation({"teller": 50}), {"teller": 4.0})
    queue = result.per_queue["teller"]
    assert 0.0 <= queue.utilization < 0.05
    assert queue.end_backlog == 0
    assert queue.avg_wait_minutes == 0.0
    assert result.branch_wide.overloaded_slot_count == 0


def test_staff_increase_reduces_or_maintains_wait_time():
    """Adding staff to a congested queue must not increase average or p95 wait time."""
    forecast = _forecast_for({"teller": [15.0, 15.0, 15.0, 15.0]})
    services = {"teller": 4.0}
    r_low = simulate(forecast, _allocation({"teller": 1}), services)
    r_high = simulate(forecast, _allocation({"teller": 3}), services)
    assert r_high.branch_wide.avg_wait_minutes <= r_low.branch_wide.avg_wait_minutes
    assert r_high.branch_wide.p95_wait_minutes <= r_low.branch_wide.p95_wait_minutes
    assert r_high.branch_wide.overloaded_slot_count <= r_low.branch_wide.overloaded_slot_count


def test_simulation_result_serialization_roundtrip():
    """SimulationResult can be serialized to dict and reconstructed without data loss."""
    forecast = _forecast_for({"teller": [3.0, 4.0], "loans": [1.0, 2.0]})
    plan = _allocation({"teller": 2, "loans": 1})
    services = {"teller": 4.0, "loans": 15.0}
    result = simulate(forecast, plan, services)
    dumped = result.model_dump()
    reconstructed = SimulationResult(**dumped)
    assert result == reconstructed

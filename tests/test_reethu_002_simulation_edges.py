"""REETHU-002: Simulation edge-case and invariant validation."""

from backend.models import AllocationPlan, ForecastResult
from backend.simulation.engine import simulate


def forecast_for(arrivals):
    n = len(next(iter(arrivals.values())))
    slots = [f"09:{15 * i:02d}" for i in range(n)]
    return ForecastResult(scenario_name="normal", slots=slots, expected_arrivals=arrivals)


def allocation(staff, label="baseline"):
    return AllocationPlan(label=label, staff_by_queue=staff)


def test_negative_staff_rejected():
    try:
        simulate(forecast_for({"teller": [1.0]}), allocation({"teller": -1}), {"teller": 4.0})
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError("negative staff must raise ValueError")


def test_missing_service_time_rejected():
    try:
        simulate(forecast_for({"teller": [1.0]}), allocation({"teller": 1}), {})
    except ValueError as exc:
        assert "avg_service_times" in str(exc)
    else:
        raise AssertionError("missing service time must raise ValueError")


def test_zero_service_time_rejected():
    try:
        simulate(forecast_for({"teller": [1.0]}), allocation({"teller": 1}), {"teller": 0.0})
    except ValueError as exc:
        assert "must be > 0" in str(exc)
    else:
        raise AssertionError("zero service time must raise ValueError")


def test_zero_staff_backlog_grows_and_equals_total_arrivals():
    result = simulate(forecast_for({"teller": [1.0, 2.0, 3.0]}), allocation({"teller": 0}), {"teller": 4.0})
    queue = result.per_queue["teller"]
    assert queue.total_served == 0
    assert queue.end_backlog == 6
    assert queue.overloaded_slots


def test_overload_labels_are_forecast_slots():
    forecast = forecast_for({"teller": [10.0, 10.0]})
    result = simulate(forecast, allocation({"teller": 0}), {"teller": 4.0})
    assert set(result.per_queue["teller"].overloaded_slots).issubset(set(forecast.slots))


def test_branch_overload_count_is_unique_slot_union():
    forecast = ForecastResult(
        scenario_name="normal", slots=["09:00"],
        expected_arrivals={"teller": [10.0], "loans": [10.0]},
    )
    result = simulate(forecast, allocation({"teller": 0, "loans": 0}), {"teller": 4.0, "loans": 15.0})
    assert result.branch_wide.overloaded_slot_count == 1


def test_p95_wait_is_at_least_average_wait():
    result = simulate(forecast_for({"teller": [1.0, 8.0, 8.0]}), allocation({"teller": 1}), {"teller": 4.0})
    queue = result.per_queue["teller"]
    assert queue.p95_wait_minutes >= queue.avg_wait_minutes >= 0
    assert result.branch_wide.p95_wait_minutes >= result.branch_wide.avg_wait_minutes >= 0


def test_utilization_is_between_zero_and_one():
    result = simulate(forecast_for({"teller": [100.0]}), allocation({"teller": 1}), {"teller": 1.0})
    assert 0.0 <= result.per_queue["teller"].utilization <= 1.0


def test_simulation_is_deterministic():
    forecast = forecast_for({"teller": [2.0, 5.0, 1.0]})
    plan = allocation({"teller": 1})
    assert simulate(forecast, plan, {"teller": 4.0}) == simulate(forecast, plan, {"teller": 4.0})


def test_single_slot_horizon_is_supported():
    result = simulate(forecast_for({"teller": [2.0]}), allocation({"teller": 1}), {"teller": 4.0})
    assert result.per_queue["teller"].total_served >= 0
    assert result.per_queue["teller"].end_backlog >= 0

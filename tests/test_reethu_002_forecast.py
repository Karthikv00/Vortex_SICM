"""REETHU-002: Forecasting contract and integration validation.

Covers the forecasting-layer contracts, edge cases, and simulation handoff
without modifying production behavior.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.forecasting.forecast import forecast
from backend.models import AllocationPlan, ForecastResult, QueueConfig, ScenarioConfig
from backend.simulation.engine import simulate
from data.scenarios import get_scenario


SCENARIOS = ("normal", "peak", "surge")


def _service_times(scenario: ScenarioConfig) -> dict[str, float]:
    return {q.queue_id: q.avg_service_time_minutes for q in scenario.queues}


def _adequate_allocation(scenario: ScenarioConfig) -> AllocationPlan:
    # Allocate the minimum valid staff to every canonical queue.
    return AllocationPlan(
        label="baseline",
        staff_by_queue={q.queue_id: q.min_staff for q in scenario.queues},
    )


def test_forecast_returns_forecast_result_for_all_scenarios():
    """forecast() returns the current ForecastResult model for each scenario."""
    for name in SCENARIOS:
        result = forecast(get_scenario(name, seed=42))
        assert isinstance(result, ForecastResult)
        assert result.scenario_name == name


def test_forecast_slot_count_matches_scenario():
    """Forecast slot count must match ScenarioConfig.slot_count()."""
    for name in SCENARIOS:
        scenario = get_scenario(name, seed=42)
        result = forecast(scenario)
        assert len(result.slots) == scenario.slot_count()
        assert all(
            len(values) == len(result.slots)
            for values in result.expected_arrivals.values()
        )


def test_forecast_values_are_non_negative():
    """Forecast smoothing must never produce negative arrival values."""
    for name in SCENARIOS:
        result = forecast(get_scenario(name, seed=42))
        assert all(
            value >= 0
            for values in result.expected_arrivals.values()
            for value in values
        )


def test_forecast_is_deterministic_for_same_scenario_and_seed():
    """Identical ScenarioConfig inputs produce identical forecasts."""
    for name in SCENARIOS:
        first = forecast(get_scenario(name, seed=123))
        second = forecast(get_scenario(name, seed=123))
        assert first == second


def test_forecast_changes_when_seed_changes():
    """Seeded generator variation is preserved through forecasting."""
    first = forecast(get_scenario("normal", seed=42))
    second = forecast(get_scenario("normal", seed=999))
    assert first.expected_arrivals != second.expected_arrivals


def test_forecast_preserves_queue_set():
    """Forecast keeps every queue defined by the scenario."""
    for name in SCENARIOS:
        scenario = get_scenario(name, seed=42)
        result = forecast(scenario)
        assert set(result.expected_arrivals) == set(scenario.queue_ids())


def test_forecast_preserves_slot_labels_from_generator():
    """Forecast keeps the generated HH:MM slot labels and their ordering."""
    result = forecast(get_scenario("normal", seed=42))
    assert result.slots[0] == "09:00"
    assert result.slots[-1] == "16:45"
    assert all(len(slot) == 5 and slot[2] == ":" for slot in result.slots)
    assert result.slots == sorted(result.slots)


def test_forecast_smoothing_preserves_list_length():
    """The rolling forecast transformation preserves each queue's slot count."""
    scenario = get_scenario("surge", seed=42)
    result = forecast(scenario)
    expected_count = scenario.slot_count()
    for values in result.expected_arrivals.values():
        assert len(values) == expected_count


def test_forecast_output_feeds_simulation_without_transformation():
    """A real ForecastResult can be consumed directly by simulate()."""
    scenario = get_scenario("normal", seed=42)
    result = forecast(scenario)
    simulation = simulate(
        forecast=result,
        allocation=_adequate_allocation(scenario),
        avg_service_times=_service_times(scenario),
        slot_minutes=scenario.slot_minutes,
    )
    assert set(simulation.per_queue) == set(scenario.queue_ids())
    assert simulation.branch_wide.total_served >= 0


def test_forecast_is_valid_for_single_slot_horizon():
    """A one-slot ScenarioConfig produces a valid one-slot ForecastResult."""
    base = get_scenario("normal", seed=42)
    scenario = base.model_copy(update={"horizon_start": "09:00", "horizon_end": "09:15"})
    result = forecast(scenario)
    assert len(result.slots) == 1
    assert result.slots == ["09:00"]
    assert all(len(values) == 1 for values in result.expected_arrivals.values())
    assert all(value >= 0 for values in result.expected_arrivals.values() for value in values)


def test_forecast_result_rejects_mismatched_arrival_lengths():
    """The ForecastResult contract rejects queue lists with wrong lengths."""
    with pytest.raises(ValidationError, match="entries but slots has"):
        ForecastResult(
            scenario_name="normal",
            slots=["09:00", "09:15"],
            expected_arrivals={"teller": [1.0]},
        )


def test_forecast_result_rejects_negative_arrivals():
    """The ForecastResult contract rejects negative arrival values."""
    with pytest.raises(ValidationError, match="negative"):
        ForecastResult(
            scenario_name="normal",
            slots=["09:00"],
            expected_arrivals={"teller": [-1.0]},
        )


def test_forecast_rejects_scenario_with_no_queues():
    """Forecasting requires at least one queue configured in the scenario."""
    empty_scenario = ScenarioConfig.model_construct(
        scenario_name="normal",
        seed=42,
        horizon_start="09:00",
        horizon_end="10:00",
        slot_minutes=15,
        queues=[],
        total_staff_available=5,
    )
    with pytest.raises(ValueError, match="at least one queue"):
        forecast(empty_scenario)


def test_forecast_supports_custom_horizon_and_slot_size():
    """Custom 30-minute slot horizon produces correct slot counts and non-negative arrivals."""
    scenario = ScenarioConfig(
        scenario_name="normal",
        seed=42,
        horizon_start="09:00",
        horizon_end="12:00",
        slot_minutes=30,
        queues=[
            QueueConfig(
                queue_id="teller",
                name="Teller",
                min_staff=1,
                max_staff=4,
                avg_service_time_minutes=4.0,
            )
        ],
        total_staff_available=3,
    )
    result = forecast(scenario)
    assert len(result.slots) == 6
    assert result.slots == ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]
    assert len(result.expected_arrivals["teller"]) == 6
    assert all(v >= 0 for v in result.expected_arrivals["teller"])


def test_forecast_serialization_roundtrip():
    """ForecastResult can be serialized to dict and reconstructed without loss."""
    scenario = get_scenario("peak", seed=42)
    result = forecast(scenario)
    dumped = result.model_dump()
    reconstructed = ForecastResult(**dumped)
    assert result == reconstructed

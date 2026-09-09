"""
tests/test_forecasting.py — Demand forecasting regression tests.

Covers: KARTHI-004 forecasting requirements:
  - Determinism
  - Scenario-awareness (through generator pipeline)
  - Time-of-day variation
  - Multiple queues / multiple slots / single slot
  - Zero demand handling
  - Rolling-average smoothing
  - ForecastResult compatibility
  - Forecast → Simulation integration

All scenario scaling (normal/peak/surge) and time-of-day shaping is performed
by the data generator.  The forecasting layer applies deterministic smoothing
and returns a valid ForecastResult.  _FORECAST_MULTIPLIERS are intentionally
1.0 (pass-through); these tests verify the end-to-end pipeline, not a
secondary multiplier.
"""
from __future__ import annotations

import pytest

from backend.forecasting.forecast import _rolling_average, forecast
from backend.models import (
    AllocationPlan,
    ForecastResult,
    QueueConfig,
    ScenarioConfig,
)
from backend.simulation.engine import simulate
from data.scenarios import normal_scenario, peak_scenario, surge_scenario


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_scenario(
    scenario_name: str = "normal",
    seed: int = 42,
    horizon_start: str = "09:00",
    horizon_end: str = "10:00",
    slot_minutes: int = 15,
) -> ScenarioConfig:
    """Build a small scenario for focused testing (4 slots, 1 hour)."""
    return ScenarioConfig(
        scenario_name=scenario_name,
        seed=seed,
        horizon_start=horizon_start,
        horizon_end=horizon_end,
        slot_minutes=slot_minutes,
        queues=[
            QueueConfig(
                queue_id="teller",
                name="Teller",
                min_staff=1,
                max_staff=5,
                avg_service_time_minutes=4,
            ),
        ],
        total_staff_available=3,
    )


# ---------------------------------------------------------------------------
# Basic forecast
# ---------------------------------------------------------------------------

def test_basic_forecast_returns_forecast_result():
    """forecast() returns a valid ForecastResult instance."""
    cfg = normal_scenario(seed=42)
    result = forecast(cfg)
    assert isinstance(result, ForecastResult)
    assert result.scenario_name == "normal"
    assert len(result.slots) > 0
    assert len(result.expected_arrivals) > 0


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_determinism_same_input_same_output():
    """Same scenario config → identical forecast output."""
    cfg1 = normal_scenario(seed=42)
    cfg2 = normal_scenario(seed=42)
    r1 = forecast(cfg1)
    r2 = forecast(cfg2)
    assert r1.slots == r2.slots
    assert r1.expected_arrivals == r2.expected_arrivals
    assert r1.scenario_name == r2.scenario_name


def test_repeated_execution_identical():
    """Running forecast twice on the same config produces identical results."""
    cfg = surge_scenario(seed=99)
    r1 = forecast(cfg)
    r2 = forecast(cfg)
    assert r1.model_dump() == r2.model_dump()


# ---------------------------------------------------------------------------
# Scenario behavior (verified through the generator pipeline)
# ---------------------------------------------------------------------------

def test_scenario_multiplier_normal():
    """Normal scenario produces valid non-negative forecast values."""
    cfg = normal_scenario(seed=42)
    result = forecast(cfg)
    for qid, arrivals in result.expected_arrivals.items():
        assert all(v >= 0 for v in arrivals), f"Negative value in {qid}"


def test_scenario_peak_higher_than_normal():
    """Peak total demand > normal total demand (same seed)."""
    normal_fc = forecast(normal_scenario(seed=42))
    peak_fc = forecast(peak_scenario(seed=42))
    normal_total = sum(
        sum(arrivals) for arrivals in normal_fc.expected_arrivals.values()
    )
    peak_total = sum(
        sum(arrivals) for arrivals in peak_fc.expected_arrivals.values()
    )
    assert peak_total > normal_total, (
        f"Peak total ({peak_total:.1f}) should exceed normal ({normal_total:.1f})"
    )


def test_scenario_surge_higher_than_peak():
    """Surge total demand > peak total demand (same seed)."""
    peak_fc = forecast(peak_scenario(seed=42))
    surge_fc = forecast(surge_scenario(seed=42))
    peak_total = sum(
        sum(arrivals) for arrivals in peak_fc.expected_arrivals.values()
    )
    surge_total = sum(
        sum(arrivals) for arrivals in surge_fc.expected_arrivals.values()
    )
    assert surge_total > peak_total, (
        f"Surge total ({surge_total:.1f}) should exceed peak ({peak_total:.1f})"
    )


# ---------------------------------------------------------------------------
# Time-of-day variation
# ---------------------------------------------------------------------------

def test_time_of_day_variation():
    """Forecast values should vary across time slots (not all identical)."""
    cfg = normal_scenario(seed=42)
    result = forecast(cfg)
    # Check the teller queue — should have some variation across the day
    teller = result.expected_arrivals["teller"]
    assert len(set(teller)) > 1, "Forecast values should vary across slots"


# ---------------------------------------------------------------------------
# Multiple queues
# ---------------------------------------------------------------------------

def test_multiple_queues_preserved():
    """All queue IDs from the scenario appear in the forecast output."""
    cfg = normal_scenario(seed=42)
    result = forecast(cfg)
    expected_queue_ids = {q.queue_id for q in cfg.queues}
    actual_queue_ids = set(result.expected_arrivals.keys())
    assert actual_queue_ids == expected_queue_ids


# ---------------------------------------------------------------------------
# Slot alignment
# ---------------------------------------------------------------------------

def test_slot_count_matches_scenario():
    """Forecast slot count matches the scenario's computed slot count."""
    cfg = normal_scenario(seed=42)
    result = forecast(cfg)
    expected_slot_count = cfg.slot_count()
    assert len(result.slots) == expected_slot_count
    for qid, arrivals in result.expected_arrivals.items():
        assert len(arrivals) == expected_slot_count, (
            f"Queue '{qid}' has {len(arrivals)} values, expected {expected_slot_count}"
        )


# ---------------------------------------------------------------------------
# Zero demand
# ---------------------------------------------------------------------------

def test_zero_demand_no_negative():
    """Forecast with a queue having zero base rate produces no negatives."""
    cfg = ScenarioConfig(
        scenario_name="normal",
        seed=42,
        horizon_start="09:00",
        horizon_end="10:00",
        slot_minutes=15,
        queues=[
            QueueConfig(
                queue_id="empty_queue",
                name="Empty Queue",
                min_staff=1,
                max_staff=2,
                avg_service_time_minutes=5,
            ),
        ],
        total_staff_available=1,
    )
    result = forecast(cfg)
    for qid, arrivals in result.expected_arrivals.items():
        assert all(v >= 0 for v in arrivals), f"Negative forecast in {qid}"


# ---------------------------------------------------------------------------
# Single slot
# ---------------------------------------------------------------------------

def test_single_slot_scenario():
    """Forecasting works correctly with a single time slot."""
    cfg = ScenarioConfig(
        scenario_name="normal",
        seed=42,
        horizon_start="09:00",
        horizon_end="09:15",
        slot_minutes=15,
        queues=[
            QueueConfig(
                queue_id="teller",
                name="Teller",
                min_staff=1,
                max_staff=5,
                avg_service_time_minutes=4,
            ),
        ],
        total_staff_available=2,
    )
    result = forecast(cfg)
    assert len(result.slots) == 1
    assert result.slots[0] == "09:00"
    for qid, arrivals in result.expected_arrivals.items():
        assert len(arrivals) == 1
        assert arrivals[0] >= 0


# ---------------------------------------------------------------------------
# Rolling average smoothing
# ---------------------------------------------------------------------------

def test_rolling_average_smoothing():
    """Rolling average produces expected smoothed output."""
    data = [0.0, 10.0, 0.0, 10.0, 0.0]
    smoothed = _rolling_average(data, window=3)
    assert len(smoothed) == len(data)
    # Middle element: avg of [10.0, 0.0, 10.0] = 6.67
    assert abs(smoothed[2] - (10.0 + 0.0 + 10.0) / 3) < 0.01
    # All values non-negative
    assert all(v >= 0 for v in smoothed)


def test_rolling_average_empty_input():
    """Empty input returns empty output."""
    assert _rolling_average([], window=3) == []


def test_rolling_average_single_element():
    """Single-element input returns the same element."""
    result = _rolling_average([5.0], window=3)
    assert len(result) == 1
    assert result[0] == 5.0


# ---------------------------------------------------------------------------
# ForecastResult compatibility
# ---------------------------------------------------------------------------

def test_forecast_result_compatibility():
    """Forecast output satisfies all ForecastResult model validations."""
    for scenario_fn in [normal_scenario, peak_scenario, surge_scenario]:
        cfg = scenario_fn(seed=42)
        result = forecast(cfg)
        # Re-validate through Pydantic to ensure contract compliance
        validated = ForecastResult(**result.model_dump())
        assert validated.scenario_name == cfg.scenario_name
        assert len(validated.slots) == cfg.slot_count()
        for qid in cfg.queue_ids():
            assert qid in validated.expected_arrivals
            assert len(validated.expected_arrivals[qid]) == len(validated.slots)
            assert all(v >= 0 for v in validated.expected_arrivals[qid])


# ---------------------------------------------------------------------------
# Forecast → Simulation integration
# ---------------------------------------------------------------------------

def test_forecast_to_simulation_integration():
    """Forecast output can be consumed by the simulation engine without error."""
    cfg = normal_scenario(seed=42)
    fc = forecast(cfg)
    avg_times = {q.queue_id: q.avg_service_time_minutes for q in cfg.queues}
    allocation = AllocationPlan(
        label="baseline",
        staff_by_queue={q.queue_id: q.min_staff + 1 for q in cfg.queues},
    )
    result = simulate(fc, allocation, avg_times, cfg.slot_minutes)
    # Verify result has all queues
    for q in cfg.queues:
        assert q.queue_id in result.per_queue
    # Branch-wide metrics are non-negative
    assert result.branch_wide.avg_wait_minutes >= 0
    assert result.branch_wide.total_served >= 0


# ---------------------------------------------------------------------------
# All scenarios produce valid forecasts
# ---------------------------------------------------------------------------

def test_all_scenarios_produce_valid_forecast():
    """All three canonical scenarios produce valid ForecastResult output."""
    for scenario_fn in [normal_scenario, peak_scenario, surge_scenario]:
        cfg = scenario_fn(seed=42)
        result = forecast(cfg)
        assert isinstance(result, ForecastResult)
        assert result.scenario_name == cfg.scenario_name
        assert len(result.slots) == cfg.slot_count()
        for qid in cfg.queue_ids():
            assert qid in result.expected_arrivals
            arrivals = result.expected_arrivals[qid]
            assert len(arrivals) == len(result.slots)
            assert all(v >= 0 for v in arrivals)

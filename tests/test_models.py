"""
tests/test_models.py — Validate shared Pydantic model contracts.

Tests that models validate correctly and reject invalid input.
REETHU-001 / TC coverage: KARTHI-002 contract validation.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.models import AllocationPlan, ForecastResult, QueueConfig, ScenarioConfig


def test_queue_config_min_le_max_valid():
    q = QueueConfig(queue_id="teller", name="Teller", min_staff=1, max_staff=5, avg_service_time_minutes=4)
    assert q.min_staff <= q.max_staff


def test_queue_config_min_gt_max_rejected():
    with pytest.raises(ValidationError):
        QueueConfig(queue_id="x", name="X", min_staff=5, max_staff=2, avg_service_time_minutes=4)


def test_scenario_slot_count():
    from data.scenarios import normal_scenario
    cfg = normal_scenario()
    # 09:00–17:00 = 480 min / 15 = 32 slots
    assert cfg.slot_count() == 32


def test_forecast_result_length_mismatch_rejected():
    with pytest.raises(ValidationError):
        ForecastResult(
            scenario_name="normal",
            slots=["09:00", "09:15"],
            expected_arrivals={"teller": [1, 2, 3]},  # length 3 ≠ 2
        )


def test_allocation_plan_total_staff():
    plan = AllocationPlan(label="baseline", staff_by_queue={"teller": 4, "loans": 2, "customer_service": 3})
    assert plan.total_staff() == 9


def _valid_scenario_kwargs():
    return {
        "scenario_name": "normal",
        "horizon_start": "09:00",
        "horizon_end": "17:00",
        "slot_minutes": 15,
        "queues": [
            QueueConfig(
                queue_id="teller",
                name="Teller",
                min_staff=1,
                max_staff=5,
                avg_service_time_minutes=4,
            ),
            QueueConfig(
                queue_id="loans",
                name="Loans",
                min_staff=1,
                max_staff=4,
                avg_service_time_minutes=6,
            ),
        ],
        "total_staff_available": 4,
    }


def test_scenario_invalid_time_rejected():
    data = _valid_scenario_kwargs()
    data["horizon_start"] = "invalid"

    with pytest.raises(ValidationError):
        ScenarioConfig(**data)


def test_scenario_end_before_start_rejected():
    data = _valid_scenario_kwargs()
    data["horizon_start"] = "17:00"
    data["horizon_end"] = "09:00"

    with pytest.raises(ValidationError):
        ScenarioConfig(**data)


def test_scenario_non_divisible_horizon_rejected():
    data = _valid_scenario_kwargs()
    data["horizon_end"] = "17:10"

    with pytest.raises(ValidationError):
        ScenarioConfig(**data)


def test_scenario_duplicate_queue_ids_rejected():
    data = _valid_scenario_kwargs()
    data["queues"][1] = QueueConfig(
        queue_id="teller",
        name="Loans",
        min_staff=1,
        max_staff=4,
        avg_service_time_minutes=6,
    )

    with pytest.raises(ValidationError):
        ScenarioConfig(**data)


def test_scenario_insufficient_staff_allowed_for_optimization():
    scenario = ScenarioConfig(
        scenario_name="normal",
        seed=42,
        horizon_start="09:00",
        horizon_end="10:00",
        slot_minutes=15,
        queues=[
            QueueConfig(
                queue_id="q1",
                name="Queue 1",
                min_staff=5,
                max_staff=10,
                avg_service_time_minutes=5,
            ),
            QueueConfig(
                queue_id="q2",
                name="Queue 2",
                min_staff=5,
                max_staff=10,
                avg_service_time_minutes=5,
            ),
        ],
        total_staff_available=5,
    )

    assert scenario.total_staff_available < sum(
        queue.min_staff for queue in scenario.queues
    )


def test_allocation_negative_staff_rejected():
    with pytest.raises(ValidationError):
        AllocationPlan(
            label="whatif",
            staff_by_queue={"teller": -1},
        )


def test_allocation_empty_queue_id_rejected():
    with pytest.raises(ValidationError):
        AllocationPlan(
            label="whatif",
            staff_by_queue={"": 2},
        )


def test_forecast_negative_arrivals_rejected():
    with pytest.raises(ValidationError):
        ForecastResult(
            scenario_name="normal",
            slots=["09:00", "09:15"],
            expected_arrivals={"teller": [2, -1]},
        )

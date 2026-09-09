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

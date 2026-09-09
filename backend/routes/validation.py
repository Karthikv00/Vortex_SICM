"""Shared API-boundary validation for scenario-dependent requests."""
from __future__ import annotations

from typing import Dict, Literal

from fastapi import HTTPException
from pydantic import BaseModel

from backend.models import AllocationPlan, ForecastResult, ScenarioConfig
from data.generator import generate_slot_labels


class AllocationInput(BaseModel):
    """API input parsed before scenario-dependent allocation validation."""

    label: Literal["baseline", "optimized", "whatif"]
    staff_by_queue: Dict[str, int]

    def total_staff(self) -> int:
        return sum(self.staff_by_queue.values())


def validate_forecast(scenario: ScenarioConfig, forecast: ForecastResult) -> None:
    scenario_ids = scenario.queue_ids()
    if len(set(scenario_ids)) != len(scenario_ids):
        _invalid("invalid_scenario", "scenario queue_id values must be unique", "scenario.queues")
    if forecast.scenario_name != scenario.scenario_name:
        _invalid(
            "scenario_mismatch",
            "forecast.scenario_name must match scenario.scenario_name",
            "forecast.scenario_name",
        )

    expected_slots = generate_slot_labels(scenario)
    if forecast.slots != expected_slots:
        _invalid(
            "forecast_horizon_mismatch",
            "forecast.slots must match the scenario horizon and slot_minutes",
            "forecast.slots",
        )
    if set(forecast.expected_arrivals) != set(scenario_ids):
        _invalid(
            "forecast_queue_mismatch",
            "forecast queue IDs must exactly match scenario queue IDs",
            "forecast.expected_arrivals",
        )
    if any(value < 0 for arrivals in forecast.expected_arrivals.values() for value in arrivals):
        _invalid(
            "invalid_forecast",
            "forecast arrival counts must be non-negative",
            "forecast.expected_arrivals",
        )


def validate_allocation(
    scenario: ScenarioConfig, allocation: AllocationPlan | AllocationInput
) -> None:
    scenario_ids = scenario.queue_ids()
    if set(allocation.staff_by_queue) != set(scenario_ids):
        _invalid(
            "allocation_queue_mismatch",
            "allocation queue IDs must exactly match scenario queue IDs",
            "allocation.staff_by_queue",
        )
    for queue in scenario.queues:
        staff = allocation.staff_by_queue[queue.queue_id]
        if staff < queue.min_staff or staff > queue.max_staff:
            _invalid(
                "staff_limit_violation",
                f"Queue '{queue.queue_id}' staff must be between {queue.min_staff} and {queue.max_staff}",
                f"allocation.staff_by_queue.{queue.queue_id}",
            )
    if allocation.total_staff() > scenario.total_staff_available:
        _invalid(
            "staff_budget_exceeded",
            "allocation exceeds scenario.total_staff_available",
            "allocation.staff_by_queue",
        )


def _invalid(error: str, message: str, field: str) -> None:
    raise HTTPException(status_code=422, detail={"error": error, "message": message, "field": field})

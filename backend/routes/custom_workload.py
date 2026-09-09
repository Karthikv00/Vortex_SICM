"""
backend/routes/custom_workload.py — custom task workload analysis.

Turns user-defined task demand into a deterministic branch forecast, automatically
classifies demand as normal/peak/surge, and runs the existing resource optimizer.
"""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.models import ForecastResult, OptimizationResult, ScenarioConfig
from backend.pipeline import run_decision_pipeline
from data.scenarios import get_scenario

router = APIRouter()


class CustomTask(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    customers_per_hour: float = Field(..., ge=0)
    service_minutes: float = Field(..., gt=0)


class UnifiedTask(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_type: str = Field(..., alias="taskType")
    name: str = Field(..., min_length=1, max_length=80, alias="taskName")
    customers_per_hour: float = Field(..., ge=0, alias="customersPerHour")
    service_minutes: float = Field(..., gt=0, alias="averageServiceTimeMinutes")


class CustomWorkloadRequest(BaseModel):
    tasks: Optional[List[UnifiedTask]] = None
    teller: List[CustomTask] = Field(default_factory=list)
    loans: List[CustomTask] = Field(default_factory=list)
    customer_service: List[CustomTask] = Field(default_factory=list)
    seed: int = 42

    @model_validator(mode="after")
    def populate_from_tasks(self) -> "CustomWorkloadRequest":
        if self.tasks:
            t_list = list(self.teller)
            l_list = list(self.loans)
            cs_list = list(self.customer_service)
            for t in self.tasks:
                task_obj = CustomTask(
                    name=t.name,
                    customers_per_hour=t.customers_per_hour,
                    service_minutes=t.service_minutes,
                )
                queue_id = "loans" if t.task_type in ("loan", "loans") else t.task_type
                if queue_id == "teller":
                    t_list.append(task_obj)
                elif queue_id == "loans":
                    l_list.append(task_obj)
                elif queue_id == "customer_service":
                    cs_list.append(task_obj)
            self.teller = t_list
            self.loans = l_list
            self.customer_service = cs_list
        return self


_CANONICAL_QUEUE_RATES = {
    "teller": 20.0,
    "loans": 4.8,
    "customer_service": 10.0,
}

_SCENARIO_LABELS = {
    "normal": "Normal demand",
    "peak": "Peak demand",
    "surge": "Surge demand",
}


def _classify_scenario(tasks: CustomWorkloadRequest) -> tuple[str, float]:
    """Classify demand from aggregate customers/hour against the canonical branch load."""
    custom_rates = {
        "teller": sum(t.customers_per_hour for t in tasks.teller),
        "loans": sum(t.customers_per_hour for t in tasks.loans),
        "customer_service": sum(t.customers_per_hour for t in tasks.customer_service),
    }
    canonical_total = sum(_CANONICAL_QUEUE_RATES.values())
    demand_total = sum(custom_rates.values())
    multiplier = demand_total / canonical_total if canonical_total else 0.0

    # Thresholds deliberately match the three operating bands used by the app:
    # <1.35× normal = normal, 1.35–2.25× = peak, >2.25× = surge.
    if multiplier < 1.35:
        scenario = "normal"
    elif multiplier < 2.25:
        scenario = "peak"
    else:
        scenario = "surge"
    return scenario, multiplier


def _time_shape(slot_index: int, total_slots: int) -> float:
    t = slot_index / max(total_slots - 1, 1)
    if t < 0.1:
        return 0.5 + t * 3.0
    if t < 0.40:
        return 1.0
    if t < 0.55:
        return 0.6 + (t - 0.40) * 0.8
    if t < 0.75:
        return 0.85
    return max(0.4, 0.85 - (t - 0.75) * 2.0)


def _surge_boost(slot_index: int, total_slots: int) -> float:
    t = slot_index / max(total_slots - 1, 1)
    if 0.12 <= t <= 0.62:
        centre, width = 0.37, 0.20
        return max(0.0, 1.5 * (1 - ((t - centre) / width) ** 2))
    return 0.0


def _build_custom_forecast(scenario: ScenarioConfig, tasks: CustomWorkloadRequest) -> ForecastResult:
    task_map: Dict[str, List[CustomTask]] = {
        "teller": tasks.teller,
        "loans": tasks.loans,
        "customer_service": tasks.customer_service,
    }
    slots = []
    start_h, start_m = map(int, scenario.horizon_start.split(":"))
    start_total = start_h * 60 + start_m
    for i in range(scenario.slot_count()):
        minute = start_total + i * scenario.slot_minutes
        h, m = divmod(minute, 60)
        slots.append(f"{h:02d}:{m:02d}")

    arrivals: Dict[str, List[float]] = {}
    for queue_id, queue_tasks in task_map.items():
        hourly = sum(t.customers_per_hour for t in queue_tasks)
        values = []
        for i in range(scenario.slot_count()):
            shape = _time_shape(i, scenario.slot_count())
            if scenario.scenario_name == "surge":
                shape += _surge_boost(i, scenario.slot_count())
            values.append(round(max(0.0, hourly * (scenario.slot_minutes / 60.0) * shape), 3))
        # Three-point smoothing mirrors the canonical forecast engine.
        smoothed = []
        for i in range(len(values)):
            lo, hi = max(0, i - 1), min(len(values), i + 2)
            smoothed.append(round(sum(values[lo:hi]) / (hi - lo), 3))
        arrivals[queue_id] = smoothed

    return ForecastResult(
        scenario_name=scenario.scenario_name,
        slots=slots,
        expected_arrivals=arrivals,
    )


def _apply_task_service_times(scenario: ScenarioConfig, tasks: CustomWorkloadRequest) -> ScenarioConfig:
    task_map: Dict[str, List[CustomTask]] = {
        "teller": tasks.teller,
        "loans": tasks.loans,
        "customer_service": tasks.customer_service,
    }
    queues = []
    for queue in scenario.queues:
        queue_tasks = task_map.get(queue.queue_id, [])
        total_customers = sum(t.customers_per_hour for t in queue_tasks)
        weighted_minutes = sum(t.customers_per_hour * t.service_minutes for t in queue_tasks)
        avg_service = weighted_minutes / total_customers if total_customers > 0 else queue.avg_service_time_minutes
        queues.append(queue.model_copy(update={"avg_service_time_minutes": round(avg_service, 2)}))
    return scenario.model_copy(update={"queues": queues})


@router.post("/custom-workload/analyze")
def analyze_custom_workload(req: CustomWorkloadRequest) -> dict:
    """Classify custom demand and run the existing deterministic optimizer."""
    if not any((req.teller, req.loans, req.customer_service)):
        raise HTTPException(status_code=422, detail={"error": "empty_workload", "message": "Add at least one custom task before allocating resources."})

    try:
        scenario_name, demand_multiplier = _classify_scenario(req)
        base_scenario = get_scenario(scenario_name, seed=req.seed)
        scenario = _apply_task_service_times(base_scenario, req)
        custom_forecast = _build_custom_forecast(scenario, req)
        result: OptimizationResult = run_decision_pipeline(scenario=scenario, forecast_result=custom_forecast)
        return {
            "scenario": scenario.model_dump(),
            "scenario_label": _SCENARIO_LABELS[scenario_name],
            "demand_multiplier": round(demand_multiplier, 2),
            "forecast": custom_forecast.model_dump(),
            "optimization": result.model_dump(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"error": "custom_workload_error", "message": str(exc)})
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "custom_workload_error", "message": str(exc)})

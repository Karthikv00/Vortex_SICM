"""
backend/routes/simulation.py — /api/simulate and /api/whatif endpoints.
Spec: docs/architecture/api-contract.md
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models import AllocationPlan, ForecastResult, ScenarioConfig, SimulationResult
from backend.simulation.engine import simulate
from backend.routes.validation import validate_allocation, validate_forecast

router = APIRouter()


class SimulateRequest(BaseModel):
    scenario: ScenarioConfig
    forecast: ForecastResult
    allocation: AllocationPlan


def _run_simulation(req: SimulateRequest, label_override: str | None = None) -> SimulationResult:
    validate_forecast(req.scenario, req.forecast)
    validate_allocation(req.scenario, req.allocation)
    avg_service_times = {q.queue_id: q.avg_service_time_minutes for q in req.scenario.queues}
    allocation = req.allocation
    if label_override:
        allocation = AllocationPlan(label=label_override, staff_by_queue=allocation.staff_by_queue)
    try:
        return simulate(req.forecast, allocation, avg_service_times, req.scenario.slot_minutes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "simulation_input_error", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "simulation_error", "message": str(e)})


@router.post("/simulate", response_model=SimulationResult)
def run_simulate(req: SimulateRequest) -> SimulationResult:
    """Run a simulation for an explicit allocation. FR-API-4 / FR-SIM-1–5."""
    return _run_simulation(req)


@router.post("/whatif", response_model=SimulationResult)
def run_whatif(req: SimulateRequest) -> SimulationResult:
    """
    Run a what-if simulation for a manually supplied allocation.
    Returns a SimulationResult with the same shape as /api/simulate.
    FR-API-6 / FR-WHATIF-1,2.
    """
    return _run_simulation(req, label_override="whatif")

"""
backend/routes/optimization.py — /api/optimize endpoint.
Spec: docs/architecture/api-contract.md
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models import ForecastResult, OptimizationResult, ScenarioConfig
from backend.optimization.optimizer import optimize
from backend.routes.validation import validate_forecast

router = APIRouter()


class OptimizeRequest(BaseModel):
    scenario: ScenarioConfig
    forecast: ForecastResult


@router.post("/optimize", response_model=OptimizationResult)
def run_optimize(req: OptimizeRequest) -> OptimizationResult:
    """
    Enumerate feasible allocations, score against real simulation, return best.
    FR-API-5 / FR-OPT-1–5, FR-EXP-1,2.
    """
    try:
        validate_forecast(req.scenario, req.forecast)
        return optimize(req.scenario, req.forecast)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "optimize_input_error", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "optimize_error", "message": str(e)})

"""
backend/routes/optimization.py — /api/optimize endpoint.
Spec: docs/architecture/api-contract.md
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.forecasting.forecast import ForecastValidationError
from backend.models import ForecastResult, OptimizationResult, ScenarioConfig
from backend.pipeline import run_decision_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


class OptimizeRequest(BaseModel):
    scenario: ScenarioConfig
    forecast: Optional[ForecastResult] = None


@router.post("/optimize", response_model=OptimizationResult)
def run_optimize(req: OptimizeRequest) -> OptimizationResult:
    """
    Execute complete decision pipeline: generate/validate forecast, simulate baseline,
    enumerate feasible allocations, score against real simulation, and return best.
    FR-API-5 / FR-OPT-1–5, FR-EXP-1,2.
    """
    try:
        return run_decision_pipeline(scenario=req.scenario, forecast_result=req.forecast)
    except ForecastValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={"error": e.error, "message": e.message, "field": e.field},
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "optimize_input_error", "message": str(e)},
        )
    except Exception:
        logger.exception("Optimization pipeline failed unexpectedly")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "optimize_error",
                "message": "Unable to compute optimization",
            },
        )

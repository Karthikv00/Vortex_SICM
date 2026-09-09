"""
backend/routes/forecast.py — /api/forecast endpoint.
Spec: docs/architecture/api-contract.md
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models import ForecastResult, ScenarioConfig
from backend.forecasting.forecast import forecast

router = APIRouter()
logger = logging.getLogger(__name__)


class ForecastRequest(BaseModel):
    scenario: ScenarioConfig


@router.post("/forecast", response_model=ForecastResult)
def get_forecast(req: ForecastRequest) -> ForecastResult:
    """
    Return a ForecastResult for the given ScenarioConfig.
    FR-API-3 / FR-FCST-1,2,3.
    """
    try:
        return forecast(req.scenario)
    except Exception:
        logger.exception("Forecast generation failed")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "forecast_error",
                "message": "Unable to generate forecast",
            },
        )

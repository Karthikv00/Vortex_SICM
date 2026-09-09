"""
backend/routes/scenario.py — /api/scenario/generate endpoint.
Spec: docs/architecture/api-contract.md
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from data.scenarios import get_scenario
from data.generator import generate
from backend.models import ScenarioConfig
from backend.optimization.baseline import baseline_allocation

router = APIRouter()


class GenerateRequest(BaseModel):
    scenario_name: str = "normal"
    seed: int = 42


@router.post("/scenario/generate")
def generate_scenario(req: GenerateRequest) -> dict:
    """
    Generate a ScenarioConfig, synthetic arrivals, and the authoritative
    deterministic baseline allocation for the requested scenario.
    FR-API-2 / FR-DATA-1,2,3,4.
    """
    try:
        scenario: ScenarioConfig = get_scenario(req.scenario_name, seed=req.seed)
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "invalid_scenario", "message": str(e), "field": "scenario_name"},
        )

    raw_data = generate(scenario)
    baseline = baseline_allocation(scenario)
    return {
        "scenario": scenario.model_dump(),
        "arrivals": raw_data.model_dump(),
        "baseline": baseline.model_dump(),
    }


@router.post("/scenario/baseline")
def get_baseline(scenario: ScenarioConfig) -> dict:
    """Return the authoritative deterministic baseline allocation."""
    try:
        baseline = baseline_allocation(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "infeasible_baseline", "message": str(e)},
        )
    return baseline.model_dump()

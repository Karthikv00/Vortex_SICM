"""
backend/routes/scenario.py — /api/scenario/generate endpoint.
Spec: docs/architecture/api-contract.md
"""
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from data.scenarios import get_scenario
from data.generator import generate
from backend.models import ScenarioConfig

router = APIRouter()


class GenerateRequest(BaseModel):
    scenario_name: str = "normal"
    seed: int = 42


@router.post("/scenario/generate")
def generate_scenario(req: GenerateRequest) -> dict:
    """
    Generate a ScenarioConfig + synthetic arrival data for the requested scenario.
    FR-API-2 / FR-DATA-1,2,3,4.
    """
    try:
        scenario: ScenarioConfig = get_scenario(req.scenario_name, seed=req.seed)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail={"error": "invalid_scenario", "message": str(e), "field": "scenario_name"})

    raw_data = generate(scenario)
    return {
        "scenario": scenario.model_dump(),
        "arrivals": raw_data.model_dump(),
    }

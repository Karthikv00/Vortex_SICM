"""Deterministic /api/explain endpoint."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models import OptimizationResult, ScenarioConfig
from backend.optimization.explain import explain_result
from backend.optimization.optimizer import enumerate_feasible_allocations

router = APIRouter()


class ExplainRequest(BaseModel):
    scenario: ScenarioConfig
    optimization: OptimizationResult


class ExplainResponse(BaseModel):
    explanation: str


@router.post("/explain", response_model=ExplainResponse)
def run_explain(req: ExplainRequest) -> ExplainResponse:
    """Regenerate the authoritative explanation from an optimization result."""
    if req.optimization.scenario_name != req.scenario.scenario_name:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "scenario_mismatch",
                "message": "optimization.scenario_name must match scenario.scenario_name",
                "field": "optimization.scenario_name",
            },
        )
    if not req.optimization.feasible:
        return ExplainResponse(explanation=req.optimization.explanation)

    return ExplainResponse(
        explanation=explain_result(
            scenario=req.scenario,
            base_plan=req.optimization.baseline.allocation,
            opt_plan=req.optimization.optimized.allocation,
            base_result=req.optimization.baseline.result,
            opt_result=req.optimization.optimized.result,
            breakdown=req.optimization.score_breakdown,
            improvement=req.optimization.improvement,
            n_feasible=len(enumerate_feasible_allocations(req.scenario)),
        )
    )

"""
backend/routes/stress_test.py — Branch Stress Test and Scenario Persistence routes.

Exposes endpoints for running deterministic branch stress tests, saving
scenario snapshots into Supabase, and retrieving historical runs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.persistence import db
from backend.resilience.engine import StressTestConfig, run_branch_stress_test
from backend.routes.custom_workload import UnifiedTask

router = APIRouter()


class StressTestRequest(BaseModel):
    branch_id: Optional[str] = "branch-main"
    tasks: Optional[List[UnifiedTask]] = None
    stress_config: Optional[StressTestConfig] = None


class ScenarioSaveRequest(BaseModel):
    branch_id: Optional[str] = "branch-main"
    scenario_type: Literal["baseline", "stress_test", "recovery_plan", "what_if"] = "stress_test"
    scenario_name: str = Field(..., min_length=1, max_length=120)
    input_snapshot: Dict[str, Any]
    result_snapshot: Dict[str, Any]


@router.post("/stress-test")
def execute_stress_test(req: StressTestRequest) -> Dict[str, Any]:
    """
    Run branch operational stress test across Demand, Service-Time,
    Workforce, or Combined shocks. Reuses the canonical simulation pipeline.
    """
    tasks = req.tasks
    if not tasks:
        # Load persisted tasks from branch
        persisted = db.get_branch_tasks(req.branch_id or "branch-main")
        if not persisted:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error": "empty_tasks", "message": "No tasks provided or found in branch."},
            )
        tasks = [
            UnifiedTask(
                task_type=t["task_type"],
                name=t["task_name"],
                customers_per_hour=t["customers_per_hour"],
                service_minutes=t["average_service_time_minutes"],
            )
            for t in persisted
        ]

    try:
        result = run_branch_stress_test(tasks=tasks, stress_config=req.stress_config)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error": "invalid_stress_input", "message": str(exc)})
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "stress_test_error", "message": str(exc)})


@router.post("/scenarios", status_code=status.HTTP_201_CREATED)
def save_scenario_run(req: ScenarioSaveRequest) -> Dict[str, Any]:
    """Persist a scenario run snapshot into Supabase or local store."""
    try:
        saved = db.save_scenario_run(
            branch_id=req.branch_id or "branch-main",
            scenario_type=req.scenario_type,
            scenario_name=req.scenario_name,
            input_snapshot=req.input_snapshot,
            result_snapshot=req.result_snapshot,
        )
        return saved
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "save_scenario_error", "message": str(exc)},
        )


@router.get("/branches/{branch_id}/scenarios")
def list_branch_scenarios(
    branch_id: str, scenario_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve historical saved scenario runs for a branch."""
    return db.get_scenario_runs(branch_id=branch_id, scenario_type=scenario_type)

"""
backend/routes/branches.py — Branch & Custom Task persistence routes.

Exposes REST APIs for branches, tasks, and persistence connectivity status.
Spec: JP-012 Customer Arrival Queue Simulation & Resource Allocation Optimizer
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from backend.persistence import db

router = APIRouter()


class BranchCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=150)


class BranchTaskCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_type: Literal["teller", "loan", "customer_service"] = Field(..., alias="taskType")
    task_name: str = Field(..., min_length=1, max_length=80, alias="taskName")
    customers_per_hour: float = Field(..., ge=0, alias="customersPerHour")
    average_service_time_minutes: float = Field(..., gt=0, alias="averageServiceTimeMinutes")


class BranchTaskUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_type: Optional[Literal["teller", "loan", "customer_service"]] = Field(None, alias="taskType")
    task_name: Optional[str] = Field(None, min_length=1, max_length=80, alias="taskName")
    customers_per_hour: Optional[float] = Field(None, ge=0, alias="customersPerHour")
    average_service_time_minutes: Optional[float] = Field(None, gt=0, alias="averageServiceTimeMinutes")


# ---------------------------------------------------------------------------
# Branches Endpoints
# ---------------------------------------------------------------------------
@router.get("/branches")
def list_branches() -> List[Dict[str, Any]]:
    """List all available branches."""
    return db.get_branches()


@router.post("/branches", status_code=status.HTTP_201_CREATED)
def create_branch(payload: BranchCreateRequest) -> Dict[str, Any]:
    """Create a new branch."""
    return db.create_branch(name=payload.name, location=payload.location)


# ---------------------------------------------------------------------------
# Tasks Endpoints
# ---------------------------------------------------------------------------
@router.get("/branches/{branch_id}/tasks")
def list_branch_tasks(branch_id: str) -> List[Dict[str, Any]]:
    """List all custom tasks associated with a branch."""
    return db.get_branch_tasks(branch_id=branch_id)


@router.post("/branches/{branch_id}/tasks", status_code=status.HTTP_201_CREATED)
def create_branch_task(branch_id: str, payload: BranchTaskCreateRequest) -> Dict[str, Any]:
    """Create a new task for the given branch."""
    task_data = {
        "task_type": payload.task_type,
        "task_name": payload.task_name,
        "customers_per_hour": payload.customers_per_hour,
        "average_service_time_minutes": payload.average_service_time_minutes,
    }
    return db.create_branch_task(branch_id=branch_id, task=task_data)


@router.put("/branches/{branch_id}/tasks/{task_id}")
def update_branch_task(
    branch_id: str, task_id: str, payload: BranchTaskUpdateRequest
) -> Dict[str, Any]:
    """Update an existing task."""
    updates = {}
    if payload.task_type is not None:
        updates["task_type"] = payload.task_type
    if payload.task_name is not None:
        updates["task_name"] = payload.task_name
    if payload.customers_per_hour is not None:
        updates["customers_per_hour"] = payload.customers_per_hour
    if payload.average_service_time_minutes is not None:
        updates["average_service_time_minutes"] = payload.average_service_time_minutes

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "empty_update", "message": "No valid fields provided for update."},
        )

    updated = db.update_branch_task(branch_id=branch_id, task_id=task_id, updates=updates)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "task_not_found", "message": f"Task {task_id} not found for branch {branch_id}."},
        )
    return updated


@router.delete("/branches/{branch_id}/tasks/{task_id}")
def delete_branch_task(branch_id: str, task_id: str) -> Dict[str, Any]:
    """Delete a task."""
    deleted = db.delete_branch_task(branch_id=branch_id, task_id=task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "task_not_found", "message": f"Task {task_id} not found for branch {branch_id}."},
        )
    return {"status": "deleted", "task_id": task_id}


# ---------------------------------------------------------------------------
# Persistence Status Check
# ---------------------------------------------------------------------------
@router.get("/persistence/status")
def get_persistence_status() -> Dict[str, Any]:
    """Check Supabase database connectivity."""
    return db.get_status()

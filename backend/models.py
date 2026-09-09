"""
backend/models.py — Shared Pydantic domain models.

These are the stable shared contracts used by simulation, optimization,
forecasting, API, and tests. Treat changes as breaking changes:
update data-model.md and notify teammates in the same PR.

Implements: KARTHI-002
Spec:        docs/architecture/data-model.md
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Queue configuration
# ---------------------------------------------------------------------------

class QueueConfig(BaseModel):
    """Configuration for a single service queue."""

    queue_id: str = Field(..., description="Machine-readable queue identifier, e.g. 'teller'")
    name: str = Field(..., description="Human-readable queue name, e.g. 'Teller'")
    min_staff: int = Field(..., ge=0, description="Minimum staff required when queue is open")
    max_staff: int = Field(..., ge=1, description="Maximum staff assignable to this queue")
    avg_service_time_minutes: float = Field(
        ..., gt=0, description="Average minutes to serve one customer"
    )

    @model_validator(mode="after")
    def min_le_max(self) -> "QueueConfig":
        if self.min_staff > self.max_staff:
            raise ValueError(
                f"Queue '{self.queue_id}': min_staff ({self.min_staff}) "
                f"must be <= max_staff ({self.max_staff})"
            )
        return self


# ---------------------------------------------------------------------------
# ScenarioConfig
# ---------------------------------------------------------------------------

class ScenarioConfig(BaseModel):
    """
    Top-level scenario definition.

    Describes the branch operating context, queue catalogue, and staffing
    envelope used to generate synthetic data and run the simulation.
    """

    scenario_name: Literal["normal", "peak", "surge"] = Field(
        ..., description="Demand scenario identifier"
    )
    seed: int = Field(42, description="Random seed for reproducible data generation")
    horizon_start: str = Field("09:00", description="Branch opening time HH:MM")
    horizon_end: str = Field("17:00", description="Branch closing time HH:MM")
    slot_minutes: int = Field(15, ge=5, le=60, description="Simulation slot width in minutes")
    queues: List[QueueConfig] = Field(
        ..., min_length=1, description="Ordered list of service queues"
    )
    total_staff_available: int = Field(
        ..., ge=1, description="Total staff budget across all queues"
    )

    def queue_ids(self) -> List[str]:
        return [q.queue_id for q in self.queues]

    def queue_by_id(self, queue_id: str) -> QueueConfig:
        for q in self.queues:
            if q.queue_id == queue_id:
                return q
        raise KeyError(f"Queue '{queue_id}' not found in scenario")

    def slot_count(self) -> int:
        """Number of time slots in the simulation horizon."""
        start_h, start_m = map(int, self.horizon_start.split(":"))
        end_h, end_m = map(int, self.horizon_end.split(":"))
        total_minutes = (end_h * 60 + end_m) - (start_h * 60 + start_m)
        return total_minutes // self.slot_minutes


# ---------------------------------------------------------------------------
# ForecastResult
# ---------------------------------------------------------------------------

class ForecastResult(BaseModel):
    """
    Demand forecast for one scenario.

    expected_arrivals maps queue_id → list of expected customer counts,
    one per time slot. All lists must be the same length as `slots`.
    """

    scenario_name: str
    slots: List[str] = Field(..., description="Slot labels, e.g. ['09:00', '09:15', ...]")
    expected_arrivals: Dict[str, List[float]] = Field(
        ..., description="queue_id → arrivals per slot"
    )

    @model_validator(mode="after")
    def lengths_match(self) -> "ForecastResult":
        n = len(self.slots)
        for qid, arrivals in self.expected_arrivals.items():
            if len(arrivals) != n:
                raise ValueError(
                    f"expected_arrivals['{qid}'] has {len(arrivals)} entries "
                    f"but slots has {n}"
                )
        return self


# ---------------------------------------------------------------------------
# AllocationPlan
# ---------------------------------------------------------------------------

class AllocationPlan(BaseModel):
    """
    Staff allocation across queues.

    staff_by_queue maps queue_id → number of staff assigned.
    """

    label: Literal["baseline", "optimized", "whatif"] = Field(
        ..., description="Purpose label for this allocation"
    )
    staff_by_queue: Dict[str, int] = Field(
        ..., description="queue_id → staff count"
    )

    def total_staff(self) -> int:
        return sum(self.staff_by_queue.values())


# ---------------------------------------------------------------------------
# SimulationResult
# ---------------------------------------------------------------------------

class QueueSimResult(BaseModel):
    """Per-queue simulation metrics."""

    avg_wait_minutes: float = Field(..., ge=0)
    p95_wait_minutes: float = Field(..., ge=0)
    utilization: float = Field(..., ge=0)
    overloaded_slots: List[str] = Field(default_factory=list)
    total_served: int = Field(..., ge=0)
    end_backlog: int = Field(0, ge=0, description="Unserved customers at horizon end")


class BranchWideMetrics(BaseModel):
    """Aggregated branch-wide simulation metrics."""

    avg_wait_minutes: float = Field(..., ge=0)
    p95_wait_minutes: float = Field(..., ge=0)
    overloaded_slot_count: int = Field(..., ge=0)
    total_served: int = Field(..., ge=0)
    total_end_backlog: int = Field(0, ge=0)


class SimulationResult(BaseModel):
    """Full output of one simulation run."""

    allocation_label: str
    per_queue: Dict[str, QueueSimResult]
    branch_wide: BranchWideMetrics


# ---------------------------------------------------------------------------
# OptimizationResult
# ---------------------------------------------------------------------------

class ScoreBreakdown(BaseModel):
    """Component scores used in the optimization objective."""

    wait_score: float
    overload_score: float
    utilization_score: float
    reallocation_cost: float
    total_score: float


class AllocationWithResult(BaseModel):
    """An allocation paired with its simulation result and score."""

    allocation: AllocationPlan
    result: SimulationResult
    score: float


class ImprovementSummary(BaseModel):
    """Measurable improvement of optimized over baseline."""

    avg_wait_reduction_minutes: float
    p95_wait_reduction_minutes: float
    overloaded_slots_resolved: int
    utilization_delta: float


class OptimizationResult(BaseModel):
    """Full output of one optimization run (baseline + optimized)."""

    scenario_name: str
    baseline: AllocationWithResult
    optimized: AllocationWithResult
    score_breakdown: ScoreBreakdown
    improvement: ImprovementSummary
    explanation: str
    feasible: bool


# ---------------------------------------------------------------------------
# Error response (mirrors api-contract.md error format)
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    error: str
    message: str
    field: Optional[str] = None

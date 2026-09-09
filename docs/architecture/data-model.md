# Data Model

These are the shared contracts used by backend, simulation, optimization, QA, and frontend. Treat changes as breaking changes: notify `#hackathon-command` and update the document in the same PR.

```python
# ScenarioConfig
{
  "scenario_name": "normal" | "peak" | "surge",
  "seed": int,
  "horizon_start": "09:00",
  "horizon_end": "17:00",
  "slot_minutes": 15,
  "queues": [
    {"queue_id": "teller", "name": "Teller", "min_staff": 1, "max_staff": 6,
     "avg_service_time_minutes": 4},
    {"queue_id": "loans", "name": "Loans", "min_staff": 1, "max_staff": 3,
     "avg_service_time_minutes": 15},
    ...
  ],
  "total_staff_available": 10
}

# ForecastResult
{
  "scenario_name": str,
  "slots": ["09:00", "09:15", ...],
  "expected_arrivals": {
    "teller": [4, 5, 7, ...],
    "loans": [1, 1, 2, ...]
  }
}

# AllocationPlan
{
  "label": "baseline" | "optimized" | "whatif",
  "staff_by_queue": {"teller": 4, "loans": 2, ...}
}

# SimulationResult
{
  "allocation_label": str,
  "per_queue": {
    "teller": {
      "avg_wait_minutes": 6.2,
      "p95_wait_minutes": 14.0,
      "utilization": 0.81,
      "overloaded_slots": ["11:00", "11:15"],
      "total_served": 120,
      "end_backlog": 0
    }
  },
  "branch_wide": {
    "avg_wait_minutes": 5.1,
    "p95_wait_minutes": 12.4,
    "overloaded_slot_count": 3,
    "total_served": 310,
    "total_end_backlog": 0
  }
}

# OptimizationResult
{
  "scenario_name": str,
  "baseline": {"allocation": AllocationPlan, "result": SimulationResult, "score": float},
  "optimized": {"allocation": AllocationPlan, "result": SimulationResult, "score": float},
  "score_breakdown": {
    "wait_score": float, "overload_score": float,
    "utilization_score": float, "reallocation_cost": float,
    "total_score": float
  },
  "improvement": {
    "avg_wait_reduction_minutes": float,
    "p95_wait_reduction_minutes": float,
    "overloaded_slots_resolved": int,
    "utilization_delta": float
  },
  "explanation": str,
  "feasible": bool
}
```

All time values use `HH:MM` local time. Durations are minutes. `feasible: false` means no allocation satisfies hard constraints; `optimized` should equal `baseline` and explain why. Exact runtime typing is defined by Python dataclasses/Pydantic models.

# Backend

FastAPI backend for Vortex SICM.

## Responsibilities

- Expose the `/api` application interface.
- Validate request and response contracts.
- Generate and process synthetic branch-demand scenarios.
- Forecast demand by service queue and time slot.
- Simulate queue behavior and estimate operational metrics.
- Produce baseline and resource-constrained optimized allocations.
- Generate deterministic explanations for recommendations.
- Support custom workloads, what-if analysis, branch stress testing, persistence, and resilience logic.

## Run

From the repository root:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Health check: `GET /api/health`  
API documentation: `/docs`

## Structure

- `main.py` — FastAPI application entry point
- `models.py` — shared Pydantic/domain contracts
- `forecasting/` — demand forecasting
- `simulation/` — queue simulation engine
- `optimization/` — baseline, optimizer, and explanation logic
- `routes/` — HTTP API endpoints and validation
- `pipeline.py` — end-to-end decision pipeline
- `persistence.py` — persistence helpers
- `resilience/` — stress/recovery/scoring logic

The backend is the authoritative implementation of the operational decision logic. Keep route handlers thin and preserve the separation between API contracts and domain logic.
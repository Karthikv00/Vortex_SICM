# Technical Requirements Document (TRD)

## Runtime & language
- Python 3.11+ for backend, simulation, forecasting, optimization, and data generation.
- Standard library preferred (`random`, `statistics`, `itertools`, `dataclasses`) to reduce setup friction.

## Backend
- FastAPI + uvicorn.
- Pydantic request/response models provide typed validation and OpenAPI support.

## Data
- No database required for P0. Use in-memory Python objects / JSON under `data/`.
- If P1 persistence is reached, SQLite via standard-library `sqlite3` is the planned path.

## Simulation
- Custom fixed-width time-step simulation; no external simulation dependency.

## Optimization
- Exhaustive enumeration of feasible staff allocations; no scipy.optimize, OR-Tools, or metaheuristics for P0.

## Forecasting
- Deterministic time-of-day factor × scenario multiplier, optionally blended with rolling averages when historical synthetic data exists. No ML/DL.

## Frontend
- Deepansha owns the stack. It must consume `api-contract.md` JSON and run against mocked responses before backend integration.

## Testing
- pytest for Python-side unit/integration tests.
- FastAPI TestClient/httpx for API contract tests.

## Configuration
- Overload threshold, objective weights, min/max staff, and simulation horizon live in one configuration location. No magic numbers scattered through logic.

## Error handling
- Validate at API boundaries. Internal functions raise explicit exceptions such as `InfeasibleAllocationError` rather than ambiguous sentinel values.

## Run strategy
- Local: `uvicorn backend.main:app --reload`.
- Docker optional and not on the P0 critical path.

## Observability
- Standard-library logging at INFO for request/decision events.

## Performance
- Optimization must meet the sub-3-second target at ≤6 queues and ≤20 staff.

## Security
- No secrets; `.env` must be gitignored; no auth required for P0/P1.

## Dependency policy
- New third-party dependencies require PR justification and an ADR if they materially change architecture.

# API Contract

Base: FastAPI, JSON in/out. Backing types are defined in `data-model.md`. Frontend should mock these responses before backend is live.

## GET /api/health
Response: `{"status":"ok"}`

## POST /api/scenario/generate
Request: `{"scenario_name":"peak","seed":42}`
Response: `ScenarioConfig` plus generated synthetic arrival data.

## POST /api/forecast
Request: `{"scenario": ScenarioConfig}`
Response: `ForecastResult`.

## POST /api/simulate
Request: `{"forecast": ForecastResult, "allocation": AllocationPlan}`
Response: `SimulationResult`.

## POST /api/optimize
Request: `{"scenario": ScenarioConfig, "forecast": ForecastResult}`
Response: `OptimizationResult` including baseline, optimized allocation, score breakdown, improvement, explanation, and feasibility.

## POST /api/whatif
Request: `{"forecast": ForecastResult, "allocation": AllocationPlan}`
Response: `SimulationResult`, identical in shape to `/api/simulate`.

## Error format
```json
{"error":"short machine-readable code","message":"human-readable explanation","field":"optional offending field"}
```
Use 4xx for client/input errors and 5xx only for genuine server faults.

## Versioning
No API versioning is required for the hackathon scope. Contract changes after dependents exist must be announced and documented in the same PR.

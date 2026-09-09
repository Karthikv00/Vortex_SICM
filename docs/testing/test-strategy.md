# Test Strategy

## Layers
1. Unit tests: data generation, simulation math, forecasting, optimization scoring.
2. Integration tests: simulation + optimizer and forecast → simulation pipeline.
3. Contract tests: FastAPI endpoints against `architecture/api-contract.md` using TestClient/httpx.
4. End-to-end/demo validation: full real backend + frontend flow before submission.

## Tooling
`pytest` for Python tests; FastAPI TestClient/httpx for API contracts. Frontend test framework is optional for P0.

## Ownership
Reethu owns test-suite health and edge-case coverage. Module authors write first-pass tests for their own modules; Reethu reviews/extends.

## Non-negotiable rule
Never claim a test passed unless it was actually executed.

## Coverage priorities
1. Hard-constraint violations in optimization.
2. Simulation correctness across normal/peak/surge.
3. Edge cases.
4. API contract accuracy.
5. Full demo-flow rehearsal.

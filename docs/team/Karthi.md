# Execution PRD — Karthi

## Responsibility
Backend, synthetic data, demand forecasting, queue simulation, and API integration support.

## Completed deliverables
- `KARTHI-001` Synthetic data generator — deterministic normal/peak/surge. *(Completed & merged — PR #5)*
- `KARTHI-002` Core domain models and validation. *(Completed & merged — PR #7)*
- `KARTHI-003` Deterministic 15-minute-slot simulation and validation hardening. *(Completed & merged — PR #10)*
- `KARTHI-004` Demand forecasting. *(Completed & merged — PR #13)*
- `KARTHI-005` FastAPI endpoint/error handling hardening. *(Completed & merged — PR #18; allocation validation also hardened in PR #9)*
- `KARTHI-006` Backend integration + performance validation. *(Completed — validation-only milestone; no production code changes required.)*

## KARTHI-006 validation evidence
Latest reported validation on `main`:
- Full backend regression: **231/231 passed**.
- Normal / Peak / Surge complete pipelines verified.
- Determinism: **15/15 scenario + seed checks passed**.
- Demand ordering verified: Normal < Peak < Surge where expected by the current contracts/tests.
- Optimized allocations satisfy hard staffing constraints.
- Invalid queue IDs, negative staff/arrivals, incompatible forecasts, malformed scenarios, and infeasible allocations are rejected.
- Optimized allocations were verified through the real simulator.
- Five-run seed-42 average end-to-end runtimes: **13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge**.
- FastAPI/error-handling validation: **32/32 passed**.
- No confirmed backend defect was found; no code change was required.
- Working tree was reported clean and local `main` synchronized with `origin/main`.

## Interfaces provided
`generate(scenario_config)`, `simulate(forecast, allocation) -> SimulationResult`, `forecast(scenario) -> ForecastResult`, and the FastAPI endpoint surface consumed by the decision pipeline/dashboard.

## Current responsibility
Backend implementation milestones are complete. Provide integration support to Kiran/Deepansha/Reethu when a genuine backend/API issue is identified. Do not start another backend feature without team review.

## Critical rules
- Synthetic data only; never use real customer/bank data.
- Every random operation must remain traceable to deterministic scenario inputs/seeds.
- Preserve API/data contracts.
- Do not alter forecasting/simulation behavior merely to improve demo metrics.
- Any claimed performance or operational improvement must come from actual measured execution.

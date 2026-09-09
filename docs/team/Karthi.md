# Execution PRD — Karthi

## Responsibility
Backend, synthetic data, demand forecasting, queue simulation, domain validation, and API integration support.

## Completed deliverables
- `KARTHI-001` Synthetic data generator — deterministic Normal/Peak/Surge scenarios. *(Completed & merged — PR #5)*
- `KARTHI-002` Core domain models and validation. *(Completed & merged — PR #7)*
- `KARTHI-003` Deterministic 15-minute-slot simulation and validation hardening. *(Completed & merged — PR #10)*
- `KARTHI-004` Demand forecasting with deterministic rolling-average smoothing. Generator-owned scenario/time-of-day scaling is preserved and `_FORECAST_MULTIPLIERS` remains `1.0` intentionally. *(Completed & merged — PR #13)*
- `KARTHI-005` FastAPI endpoint and safe error-handling hardening. *(Completed & merged — PR #18; API allocation validation also centralized in PR #9)*
- `KARTHI-006` Backend integration + performance validation. *(Completed — validation-only milestone; no production code changes required.)*

## KARTHI-006 validation evidence
- Full backend regression: **231/231 passed**.
- Normal / Peak / Surge complete pipelines verified.
- Determinism: **15/15 scenario+seed checks passed**.
- Seed-42 demand ordering: **Normal 213.00 < Peak 359.00 < Surge 874.17**.
- Optimized allocations satisfy queue min/max and total staff budget.
- Invalid queue IDs, negative staff/arrivals, incompatible forecasts, malformed scenarios, and infeasible allocations are rejected.
- Optimized allocations were evaluated through the real simulator.
- Five-run seed-42 average end-to-end runtime: **13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge**; maximum observed runtime **34.5 ms**.
- FastAPI/error-handling suite: **32/32 passed**.
- No confirmed backend defect was found; no code change was required.
- Working tree was clean and local `main` was synchronized with `origin/main` at validation completion.

## Canonical seed-42 behavior
- **Normal:** baseline `{teller:4, loans:3, customer_service:3}` → optimized `{teller:4, loans:1, customer_service:2}`; 211 served, 0 backlog; branch wait/p95 0/0.
- **Peak:** baseline `{teller:4, loans:3, customer_service:3}` → optimized `{teller:4, loans:2, customer_service:3}`; 362 served, 0 backlog; branch wait/p95 0/0.
- **Surge:** baseline and optimized `{teller:4, loans:3, customer_service:3}`; 730 served, 153 backlog; branch average wait 93.6552 min, p95 153.8674 min, 25 overloaded slots. The optimizer correctly keeps the baseline when it is already globally optimal under the defined objective/constraints.

## Interfaces provided
`generate(scenario_config)`, `forecast(scenario) -> ForecastResult`, `simulate(forecast, allocation) -> SimulationResult`, and the FastAPI endpoint surface consumed by the decision pipeline/dashboard.

## Current responsibility
All backend implementation milestones are complete. Support Kiran, Deepansha, and Reethu only for genuine integration/contract blockers. Do not start another backend feature without team review.

## Critical rules
- Synthetic data only; never use real customer/bank data.
- Every random operation must remain traceable to deterministic scenario inputs/seeds.
- Preserve API/data contracts and hard resource constraints.
- Do not alter forecasting/simulation behavior merely to improve demo metrics.
- Any claimed performance or operational improvement must come from actual measured execution.
- No mock/fabricated/cherry-picked metrics in the final demo path.

# Execution PRD — Deepansha

## Responsibility
Frontend/dashboard, UX/UI implementation, visualization, UI states, and real backend/API integration.

## Completed dashboard work on `DEEPANSHA-001-dashboard`
- `DEEPANSHA-001` Dashboard shell and visualization structure. Initial UI commit: `b033f45`.
- `DEEPANSHA-002` Full dashboard implementation per approved specification, including the required sections and loading/empty/error states.
- `DEEPANSHA-003` Real FastAPI integration + demo polish. Integration commit: `7609a8c`.

## Dashboard surface implemented
The branch contains the intended single-page P0 dashboard:
1. Branch overview and scenario selector.
2. Current queue cards/grid.
3. Demand forecast and forecast chart.
4. Overload alerts.
5. Baseline allocation.
6. Optimized allocation with staff deltas.
7. Before/after comparison matrix and global metrics.
8. What-if simulator.
9. Explanation/recommendation panel.

Supporting frontend pieces include React/Vite setup, header/sidebar, metric/status components, loading/empty/error states, API service, and Vite proxy configuration.

## Real API integration evidence
Deepansha verified:
- Vite production build with **48 modules**.
- Real HTTP flows through Vite proxy + FastAPI for health, scenario generation, forecast, simulate, optimize, and what-if.
- Normal/Peak/Surge live flows.
- Structured 422 behavior for invalid inputs.
- Backend-unavailable path reaches the dashboard `ErrorState`.
- Custom API integration checks.

Playwright automation was attempted, but the browser download failed with an external CDN 404. This is recorded as a tooling limitation, not a confirmed application defect.

## Current branch/release status
The dashboard branch currently compares as **7 commits ahead of `main` and 19 commits behind `main`**. It contains the dashboard implementation, but it is **not yet merged into `main`**.

Immediate next steps:
1. Synchronize/rebase with the latest `main` as needed while preserving dashboard WIP.
2. Open the dashboard PR to `main`.
3. Obtain review and resolve genuine integration issues.
4. Remove any remaining mock/hard-coded result path from the final/demo execution path.
5. Let Reethu perform final integrated browser/QA validation after the reviewed dashboard reaches the release baseline.

## Backend integration contract
Use the existing FastAPI/backend as the source of truth:

`dashboard controls → FastAPI → DecisionPipeline → real result → dashboard visualization`

Do not duplicate forecasting, simulation, optimization, or KPI calculations in the frontend.

## Required final/demo behavior
- Scenario selection: Normal / Peak / Surge.
- Real forecast output.
- Real baseline vs optimized allocation/results.
- Waiting-time metrics.
- Overload/backlog/utilization metrics supplied by the API.
- Measured before/after improvement.
- Deterministic recommendation/explanation.
- Real what-if result where supported.
- Explicit loading, empty/invalid, server-error, and retry/recovery states.

## Critical rules
- No mock data in the final/demo execution path.
- Do not fabricate or hard-code metrics.
- Do not reproduce backend business logic in frontend code.
- Reuse the current API/data contracts.
- If a required field is missing, coordinate with Kiran rather than silently calculating it in the UI.
- Keep the demo story focused: **problem → forecast → bottleneck → recommendation → measurable impact → what-if**.

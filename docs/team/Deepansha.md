# Execution PRD — Deepansha

## Responsibility
Frontend/dashboard, UX/UI implementation, visualization, UI states, and real backend/API integration.

## Completed dashboard work on `DEEPANSHA-001-dashboard`
- `DEEPANSHA-001` Dashboard shell and visualization structure. Initial UI commit: `b033f45`.
- `DEEPANSHA-002` Full dashboard implementation per approved specification, including the required sections and loading/empty/error states.
- `DEEPANSHA-003` Real FastAPI integration + demo polish. Integration commit: `7609a8c`.

## Dashboard surface implemented
1. Branch overview and scenario selector.
2. Current queue cards/grid.
3. Demand forecast and forecast chart.
4. Overload alerts.
5. Baseline allocation.
6. Optimized allocation with staff deltas.
7. Before/after comparison matrix and global metrics.
8. What-if simulator.
9. Explanation/recommendation panel.

Supporting pieces: React/Vite setup, header/sidebar, metric/status components, loading/empty/error states, API service, and Vite proxy.

## Real API integration evidence
Deepansha reported:
- Vite production build with **48 modules**.
- Real HTTP flows through Vite proxy + FastAPI for health, scenario generation, forecast, simulate, optimize, and what-if.
- Normal/Peak/Surge live flows.
- Structured 422 behavior for invalid inputs.
- Backend-unavailable path reaches the dashboard `ErrorState`.
- Custom API integration checks.

Playwright automation was attempted, but browser download failed with an external CDN 404. This is a tooling limitation, not a confirmed application defect. Manual browser validation remains a release gate.

## Current branch/release status
Current GitHub comparison against `main` is **7 commits ahead and 30 commits behind**. No PR currently exists for `DEEPANSHA-001-dashboard`.

Immediate next steps:
1. Synchronize/rebase the feature branch with current `main` while preserving WIP.
2. Inspect the merged result for conflicts and API-contract drift.
3. Open a PR to `main` and obtain teammate review.
4. Verify the final/demo execution path is live-API-only. `frontend/src/mocks/mockData.js` exists on the branch, so confirm it is not used by the release/demo path.
5. Hand the reviewed release baseline to Reethu for final browser/integration QA.

## Backend integration contract

`dashboard controls → FastAPI → DecisionPipeline → real result → dashboard visualization`

Do not duplicate forecasting, simulation, optimization, or KPI calculations in frontend code.

## Required final/demo behavior
- Scenario selection: Normal / Peak / Surge.
- Real forecast output.
- Real baseline vs optimized allocation/results.
- Waiting-time metrics.
- Overload/backlog/utilization metrics supplied by the API.
- Measured before/after improvement.
- Deterministic recommendation/explanation.
- Real what-if result where supported.
- Loading, empty/invalid, server-error, and retry/recovery states.

## Critical rules
- No mock data in the final/demo execution path.
- Do not fabricate or hard-code metrics.
- Do not reproduce backend business logic in frontend code.
- Reuse the current API/data contracts.
- If a required field is missing, coordinate with Kiran rather than silently calculating it in the UI.
- Keep the demo story focused: **problem → forecast → bottleneck → recommendation → measurable impact → what-if**.

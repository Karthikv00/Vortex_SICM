# Execution PRD — Deepansha

## Responsibility
Frontend/dashboard, UI states, visualization, UX implementation, and real backend integration.

## Deliverable status
- `DEEPANSHA-001` Dashboard shell + visualization structure. **Complete on feature branch.** Initial dashboard UI commit: `b033f45`.
- `DEEPANSHA-002` Full dashboard per approved design, including required sections and loading/empty/error states. **Complete on feature branch.**
- `DEEPANSHA-003` Real FastAPI integration + demo polish. **Implemented and pushed on feature branch** as commit `7609a8c`; awaiting PR/reviewer integration into `main`.

## Current feature branch
- Branch: `DEEPANSHA-001-dashboard`
- Deepansha synchronized WIP with latest `origin/main` by stashing WIP, merging the current main, and restoring the stash.
- Local `skillset-dashboard/` is untracked scratch material and is not part of the task commit.

## Backend integration baseline
The backend P0 path is implemented and validated on `main`:
`synthetic data → forecast → simulation → baseline → optimization → comparison → explanation → API → validation`.

Latest backend evidence includes **231/231 tests passed**, 15/15 deterministic scenario+seed checks, hard staffing-constraint validation, real-simulator optimizer validation, and five-run average end-to-end runtimes of **13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge**. KIRAN-003 API/DecisionPipeline hardening is merged in PR #20, and REETHU-P8 validation is merged in PR #19.

The dashboard must consume these existing API/data contracts rather than reproduce backend logic.

## DEEPANSHA-003 implementation outcome
The real dashboard integration has been implemented on `DEEPANSHA-001-dashboard`.

Verified integration behavior:
- `/api/scenario/generate` response is correctly unwrapped from `{scenario, arrivals}` to the canonical `ScenarioConfig` used by the dashboard flow.
- `/api/simulate` sends `scenario + forecast + allocation`.
- `/api/whatif` sends `scenario + forecast + allocation`.
- `/api/optimize` synchronizes dashboard baseline/allocation/result from backend output.
- Live API mode is enabled by default.
- Real API errors surface through the dashboard rather than silently falling back to mocks.
- Initial baseline allocation is request construction only; backend remains the source of truth for simulation and optimization.

## Frontend validation evidence
- Vite production build passed: **48 modules transformed successfully**.
- Real HTTP flows verified through Vite proxy + FastAPI for health, scenario generation, forecast, simulate, optimize, and what-if.
- Normal / Peak / Surge live flows verified.
- Invalid scenario, unknown queue, and over-capacity staff inputs returned structured **422** responses.
- Backend-unavailable behavior surfaced through the dashboard `ErrorState`.
- Custom API integration verification passed.
- Playwright browser automation was attempted, but browser download failed because an external CDN returned **404**. This is a tooling limitation, not a confirmed application failure.

## Measured live examples
Using the real backend/API path:
- **Normal:** 213 arrivals; baseline 0 overloaded slots; 0.0 min average wait; optimized allocation `{teller: 4, loans: 1, customer_service: 2}`.
- **Peak:** 359 arrivals; baseline 0 overloaded slots; 0.0 min average wait; optimized allocation `{teller: 4, loans: 2, customer_service: 3}`.
- **Surge:** 874 arrivals; baseline 93.7 min average wait; 153.9 min p95; 25 overloaded slots; 730 served. What-if allocation `{teller: 5, loans: 2, customer_service: 3}` reduced average wait to 76.7 min and increased served customers to 752.

These are validation observations, not values to hard-code. The final dashboard must continue to render values from the live backend.

## Current acceptance gate
The implementation is ready for PR/review, but final release acceptance is not yet signed off. Before merge/release:
1. Open the feature PR from `DEEPANSHA-001-dashboard` to `main`.
2. Obtain teammate/reviewer approval before merge.
3. Re-run the dashboard against the current backend after any main changes.
4. Confirm browser console/network cleanliness manually where Playwright cannot provide coverage.
5. Verify loading, empty/invalid, server-error, and retry/recovery states manually.
6. Keep the final/demo execution path free of mock data.

## Integration rules
- No mock data in the final/demo execution path.
- Do not put simulation, forecasting, optimization, or KPI calculations in frontend code.
- Reuse the current API/data contracts. If a required response field is missing, coordinate with Kiran rather than inventing frontend calculations.
- Verify locally against a running FastAPI instance using real responses.
- Keep the demo story focused: **problem → forecast → bottleneck → recommendation → measurable impact → what-if**.
- Avoid unnecessary frontend architecture changes.

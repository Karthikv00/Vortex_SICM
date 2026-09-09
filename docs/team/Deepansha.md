# Execution PRD — Deepansha

## Responsibility
Frontend/dashboard, UI states, visualization, UX implementation, and real backend integration.

## Completed deliverables
- `DEEPANSHA-001` Dashboard shell + mock API layer. *(Completed; initial UI commit `b033f45`.)*
- `DEEPANSHA-002` Full dashboard per approved design, including loading/empty/error states. *(Completed on `DEEPANSHA-001-dashboard`.)*
- `DEEPANSHA-003` Real FastAPI integration + demo polish. *(Implemented and pushed as commit `7609a8c`; awaiting PR/reviewer integration.)*

## Backend integration baseline
Latest `main` includes KIRAN-003 API/DecisionPipeline hardening (PR #20), Karthi backend integration/performance validation, and Reethu pre-demo validation (PR #19). The backend suite is at **231/231 tests passed**. Normal/Peak/Surge pipelines, 15/15 determinism checks, hard resource constraints, real-simulator optimizer validation, and performance benchmarks were reported passing, with no confirmed backend defects.

## DEEPANSHA-003 implementation
The dashboard now consumes the real FastAPI contract instead of silently relying on mock/demo results.

Key fixes:
- `/api/scenario/generate` is correctly unwrapped from `{scenario, arrivals}` to the canonical `ScenarioConfig`.
- `/api/simulate` sends `scenario + forecast + allocation` as required by the current backend.
- `/api/whatif` sends `scenario + forecast + allocation` as required by the current backend.
- `/api/optimize` results synchronize the dashboard baseline/allocation/result with backend-computed optimization output.
- Live API mode is enabled by default.
- Real API failures now surface as dashboard errors instead of silently falling back to mocks.
- Initial baseline allocation is derived only to construct a valid simulation request; optimization remains the backend source of truth.

## Validation completed
- Production frontend build passes with Vite 5.4.21; 48 modules transformed successfully.
- Health, scenario generation, forecast, simulation, optimize, and what-if all returned successful real API responses through the Vite proxy + FastAPI.
- Normal/Peak/Surge live flows were verified.
- Invalid scenario, unknown queue, and over-capacity staff inputs returned structured 422 responses.
- Backend-unavailable behavior surfaced through the dashboard `ErrorState`.
- Custom API integration verification passed.
- Playwright browser verification was attempted, but browser download failed because the external CDN returned 404; no application defect was established from that tooling failure.

## Observed live verification examples
- NORMAL: 213 arrivals; baseline 0 overloaded slots and 0.0 min average wait; optimized allocation `{teller:4, loans:1, customer_service:2}`.
- PEAK: 359 arrivals; baseline 0 overloaded slots and 0.0 min average wait; optimized allocation `{teller:4, loans:2, customer_service:3}`.
- SURGE: 874 arrivals; baseline 93.7 min average wait, 153.9 min p95 wait, 25 overloaded slots, 730 served; what-if `{teller:5, loans:2, customer_service:3}` reduced average wait to 76.7 min and increased served customers to 752.

## Integration rules
- No mock data in the final/demo execution path.
- Do not put simulation, forecasting, optimization, or KPI calculations in frontend code.
- Reuse the current API/data contracts.
- Backend remains the source of truth for simulation and optimization results.
- Verify locally against real FastAPI responses.
- Keep the demo story focused: **problem → forecast → bottleneck → recommendation → measurable impact → what-if**.
- Preserve teammate work and keep task-scoped commits.

## Current acceptance gate
The real dashboard path is implemented and pushed. Next: open PR from `DEEPANSHA-001-dashboard` to `main`, obtain teammate/reviewer approval, then proceed to Reethu's final integrated QA, browser validation, clean-clone validation, demo rehearsal, and release sign-off.

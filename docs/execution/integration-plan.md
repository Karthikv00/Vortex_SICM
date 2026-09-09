# Integration Plan

## Principle
Each module is independently testable before integration. The backend is the source of truth; the frontend visualizes real API results and does not reproduce simulation, forecasting, optimization, or KPI logic.

## Current integration baseline
`main` contains the complete backend P0 path plus automated pre-demo validation:

`synthetic data → forecast → simulation → baseline → optimization → comparison → explanation → FastAPI → validation`

Latest backend evidence: **231/231 tests passed**, 15/15 determinism checks, hard resource constraints, real-simulator optimizer validation, and seed-42 average end-to-end runtimes of 13.7 ms Normal, 16.5 ms Peak, and 32.0 ms Surge.

## Frontend integration status
Deepansha's `DEEPANSHA-001-dashboard` branch contains the implemented real FastAPI integration (`7609a8c`). It has been validated through Vite proxy + FastAPI for health, scenario generation, forecast, simulate, optimize, and what-if; Normal/Peak/Surge live flows; structured 422 handling; and backend-unavailable `ErrorState` behavior.

Verified integration fixes:
- `/api/scenario/generate` response is unwrapped from `{scenario, arrivals}` to canonical `ScenarioConfig`.
- `/api/simulate` sends `scenario + forecast + allocation`.
- `/api/whatif` sends `scenario + forecast + allocation`.
- `/api/optimize` synchronizes dashboard baseline/allocation/result from backend output.
- Live API mode is enabled by default.
- Real API errors surface instead of silently falling back to mocks.
- Backend remains the source of truth for simulation/optimization.

Vite production build passed with **48 modules transformed**. Playwright browser automation could not complete because its browser download returned external CDN **404**; this is a tooling limitation and does not constitute an application failure. Manual browser verification remains required.

## Integration checkpoints
- **C1:** Simulation standalone validation — complete.
- **C2:** Optimizer validated against real simulation — complete.
- **C3:** FastAPI contract validation — complete.
- **C4:** Dashboard real-API swap — implemented on Deepansha feature branch; PR/review/merge pending.
- **C5:** Full browser/live-demo validation — pending manual browser verification after dashboard merge.
- **C6:** Clean-clone + final rehearsal — pending.

## Current release sequence
1. Deepansha opens `DEEPANSHA-001-dashboard` → `main` PR and obtains review.
2. Merge only after teammate/reviewer approval and contract/test evidence.
3. Reethu runs final integrated QA against the merged dashboard.
4. Re-run the full regression suite after frontend merge.
5. Manually verify browser console/network, loading/empty/error/retry states, and frontend-visible metric traceability.
6. Perform clean-clone setup/test/demo and at least two rehearsals.
7. Freeze the exact submitted version only after the rehearsed version is reproducible.

## Mocking policy
Mocks were appropriate during dashboard development only. They must not remain as a fallback in the final/demo execution path. Final/demo results must come from the real FastAPI backend.

## Contract drift
1. Announce deviations before merge.
2. Update the contract documentation in the same PR when a contract change is actually required.
3. Notify all dependents.

Never allow silent contract drift.

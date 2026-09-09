# Integration Plan

## Principle
Each module is independently testable before integration. The backend remains the source of truth. Integration must use the real API and real deterministic outputs on the release/demo path.

## Current state
- Backend/API P0 integration is complete and validated.
- REETHU-P8 live FastAPI integration validation is merged: 19/19 focused tests and 231/231 full suite at merge point.
- Deepansha has implemented the dashboard and real FastAPI client on `DEEPANSHA-001-dashboard`.
- Current GitHub branch comparison: dashboard is 7 commits ahead and 30 commits behind `main`; no PR exists yet.
- `frontend/src/mocks/mockData.js` exists on the feature branch, but the final/demo execution path must use live API responses only.

## Integration contract
`dashboard controls → FastAPI → DecisionPipeline → real result → dashboard visualization`

Required live endpoints/flows include health, scenario generation, forecast, simulate, optimize, and what-if. Frontend must not duplicate forecast, simulation, optimization, or KPI calculations.

## Checkpoints
- **C1:** Core data/domain/simulation independently validated.
- **C2:** Optimizer validated against the real simulation and hard constraints.
- **C3:** FastAPI contract and error boundaries validated.
- **C4:** P8 live backend integration validated across Normal/Peak/Surge.
- **C5:** Dashboard real-API implementation validated on feature branch.
- **C6 — current:** synchronize dashboard with current `main`, open/review/merge PR, then execute final browser QA and full regression.

## Contract drift
1. Announce deviations before merge.
2. Update the contract doc in the same PR when a contract genuinely changes.
3. Ping all dependents.

Never allow silent contract drift or frontend-side reimplementation of backend business logic.

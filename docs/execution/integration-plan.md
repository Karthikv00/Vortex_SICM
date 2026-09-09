# Integration Plan

## Principle
Each module is independently testable before integration. The backend remains the source of truth. Integration uses the real API and deterministic outputs on the release/demo path.

## Mocking
Deepansha's frontend was initially built against mock/fixture data matching the API contract. The final dashboard path now uses the real FastAPI service; mock fallback is disabled for live execution.

## Checkpoints
- **C1:** End of P2 — Karthi simulation standalone tested by Reethu. **Completed.**
- **C2:** End of P4 — Kiran optimizer tested against Karthi simulation; `OptimizationResult` matches contract. **Completed.**
- **C3:** End of P5 — API contract/error behavior hardened and validated. **Completed.**
- **C4:** Start of P7 — Deepansha swapped the dashboard to real API and ran the full live flow. **Completed.**
- **C5:** End of P7 — real health/scenario/forecast/simulate/optimize/what-if flows verified for Normal/Peak/Surge; structured invalid-input responses and backend-unavailable UI state verified. **Completed on `DEEPANSHA-001-dashboard` commit `7609a8c`.**

## Live integration contract notes
- `/api/scenario/generate` returns `{scenario, arrivals, baseline}`; frontend unwraps `scenario` before downstream calls.
- `/api/scenario/baseline` returns the authoritative deterministic baseline allocation.
- `/api/simulate` and `/api/whatif` require `scenario`, `forecast`, and `allocation`; frontend sends all three.
- `/api/optimize` remains the source of truth for optimized allocation/result and the dashboard synchronizes to its returned baseline/optimized data.
- API failures are surfaced rather than silently converted to mock data.
- Structured backend validation uses the documented `detail.error`, `detail.message`, and optional `detail.field` shape.
- Frontend does not duplicate forecast, simulation, optimization, or KPI business logic.

## Validation notes
- Backend suite: 241/241 passed on the final QA snapshot.
- Frontend production build: passed with Vite 5.4.21.
- Live API integration verification: passed.
- Browser QA: Normal/Peak/Surge, optimization, What-If, rapid scenario switching, console, and network behavior verified on the final QA snapshot.

## Contract drift
1. Announce deviations before merge.
2. Update the contract doc in the same PR when a contract genuinely changes.
3. Ping all dependents.

No silent contract drift was introduced; the frontend changes align to the current backend contract.

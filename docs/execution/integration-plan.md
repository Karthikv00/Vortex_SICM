# Integration Plan

## Principle
Each module is independently testable before integration. Integration occurs at defined checkpoints.

## Mocking
Deepansha's frontend was initially built against mock/fixture data matching the API contract. The final dashboard path now uses the real FastAPI service; mock fallback is disabled for live execution.

## Checkpoints
- **C1:** End of P2 — Karthi simulation standalone tested by Reethu. **Completed.**
- **C2:** End of P4 — Kiran optimizer tested against Karthi simulation; `OptimizationResult` matches contract. **Completed.**
- **C3:** End of P5 — API contract/error behavior hardened and validated. **Completed.**
- **C4:** Start of P7 — Deepansha swapped the dashboard to real API and ran the full live flow. **Completed.**
- **C5:** End of P7 — real health/scenario/forecast/simulate/optimize/what-if flows verified for Normal/Peak/Surge; structured invalid-input responses and backend-unavailable UI state verified. **Completed on `DEEPANSHA-001-dashboard` commit `7609a8c`.**

## Live integration contract notes
- `/api/scenario/generate` returns `{scenario, arrivals}`; frontend unwraps `scenario` before downstream calls.
- `/api/simulate` and `/api/whatif` require `scenario`, `forecast`, and `allocation`; frontend now sends all three.
- `/api/optimize` remains the source of truth for optimized allocation/result and the dashboard synchronizes to its returned baseline/optimized data.
- API failures are surfaced rather than silently converted to mock data.
- Structured backend validation uses the documented `detail.error`, `detail.message`, and optional `detail.field` shape.

## Validation notes
- Backend suite: 231/231 passed.
- Frontend production build: passed with Vite 5.4.21.
- Custom live API integration verification: passed.
- Playwright browser download was blocked by an external CDN 404; this remains a tooling limitation for browser automation, not a confirmed application failure.

## Contract drift
1. Announce deviations in `#hackathon-command` before merge.
2. Update the contract doc in the same PR.
3. Ping all dependents.

No silent contract drift was introduced by DEEPANSHA-003; the frontend changes align to the current backend contract.

# Integration Plan

## Principle
Each module is independently testable before integration. Integration occurs at defined checkpoints.

## Mocking
Deepansha's `frontend/mocks/` must return fixture JSON matching `architecture/api-contract.md` exactly. When KARTHI-005 lands, swap the mock client for a real HTTP client against `http://localhost:8000`; frontend logic should not need shape changes.

## Checkpoints
- **C1:** End of P2 — Karthi simulation standalone tested by Reethu.
- **C2:** End of P4 — Kiran optimizer tested against Karthi simulation; `OptimizationResult` matches contract.
- **C3:** End of P5 — API contract-tested with FastAPI TestClient by Reethu.
- **C4:** Start of P7 — Deepansha swaps mocks for real API and runs the full demo once.
- **C5:** End of P7 — full live demo, deterministic seed, no console/server errors.

## Contract drift
1. Announce deviations in `#hackathon-command` before merge.
2. Update the contract doc in the same PR.
3. Ping all dependents.

Never allow silent contract drift.

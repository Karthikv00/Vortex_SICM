# Execution PRD — Reethu

## Responsibility
QA, scenario realism, integration validation, regression protection, documentation/code-drift monitoring, demo validation, and release-readiness verification.

## Completed deliverables
- `REETHU-001` Generator validation scaffolding. *(Completed & merged — PR #6)*
- `REETHU-002` Forecast/simulation edge-case validation suite. *(Completed & merged — PR #15)*
- `REETHU-003` Demo scenario realism and deterministic validation. *(Completed & merged — PR #11; explanation alignment completed via PR #14)*
- `REETHU-004` Documentation/code-drift reconciliation. *(Completed & merged — PR #17)*
- `REETHU-P8` Pre-demo end-to-end integration validation and checklist reconciliation. *(Completed & merged — PR #19)*
- `REETHU-005` Final QA + acceptance validation. *(Current release-gate responsibility)*

## Validation evidence
### REETHU-001
- **22/22** focused generator tests passed.
- **91/91** full tests passed at merge point.
- Covered deterministic fixed-seed behavior, Normal/Peak/Surge differences, horizon coverage, non-negative arrivals, and contract alignment.

### REETHU-002
Added **34 dedicated tests**: 15 forecast + 19 simulation. Coverage includes contracts, horizons, determinism, invalid inputs, simulation invariants, overload/utilization, serialization, zero-staff behavior, and staff/wait monotonicity.

### REETHU-003 / PR #14
Validated Normal/Peak/Surge realism, seed-42 benchmark regression, explanation traceability, what-if trade-offs, multi-seed robustness, runtime behavior, and explanation-weight alignment with optimizer constants.

### REETHU-P8
- **19/19** focused end-to-end integration tests passed.
- **231/231** full suite passed at merge point.
- Covers live FastAPI demo flow, Normal/Peak/Surge, DecisionPipeline determinism, API-boundary invalid payloads, performance SLAs, and realistic what-if capacity/trade-offs.
- No backend/frontend production behavior was modified by P8.

## Current integrated state
Latest backend validation is **231/231 passed**. Karthi's integration validation also confirmed 15/15 determinism checks, demand ordering, hard constraints, invalid-input rejection, real-simulator optimization validation, and sub-35 ms maximum runtime for the seed-42 canonical scenarios.

Deepansha has implemented the dashboard and real FastAPI integration on `DEEPANSHA-001-dashboard`. The branch is not yet merged and must be reviewed before final release validation.

## REETHU-005 release-gate checklist
1. Review the final Deepansha dashboard PR once opened.
2. Validate Normal/Peak/Surge through the real browser dashboard and live FastAPI backend.
3. Verify forecast, baseline, optimized allocation, waiting time, overload/backlog/utilization, improvement, explanation/recommendation, and supported what-if values against actual backend responses.
4. Check browser console and network behavior during the complete demo journey.
5. Manually verify loading, empty/invalid, server-error, and retry states.
6. Re-run the full regression suite after dashboard/API integration changes.
7. Perform clean-clone setup/test/demo validation.
8. Rehearse the complete demo at least twice, preferably with two people.
9. Classify failures as blocker/P0/P1/cosmetic and obtain evidence for every fix.
10. Sign off the submitted version only after reproducibility and release gates are established.

## Critical rules
- Never weaken tests to make the suite green.
- Never accept fabricated, cherry-picked, or hard-coded demo metrics.
- Treat simulation/optimization edge cases as P0 validation concerns.
- Flag API/data-contract drift immediately.
- Frontend must consume real backend results in the final/demo path.
- Final sign-off requires actual evidence and reproducibility.

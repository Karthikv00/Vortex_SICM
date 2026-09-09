# Execution PRD — Reethu

## Responsibility
QA, scenario realism, integration validation, demo validation, regression protection, and release-readiness verification.

## Completed deliverables
- `REETHU-001` Generator validation scaffolding. *(Completed & merged — PR #6)*
- `REETHU-002` Forecast/simulation edge-case validation. *(Completed & merged — PR #15)*
- `REETHU-003` Demo scenario realism and validation. *(Completed & merged — PR #11; explanation alignment completed in PR #14.)*
- `REETHU-004` Documentation/code-drift reconciliation. *(Completed & merged — PR #17)*
- `REETHU-P8` Pre-demo end-to-end integration validation and checklist reconciliation. *(Completed & merged — PR #19)*

## REETHU-P8 validation evidence
PR #19 added `tests/test_reethu_p8_integration.py` with 19 end-to-end integration tests covering the live FastAPI demo flow across Normal/Peak/Surge, DecisionPipeline determinism, malformed/invalid API payload handling, performance SLAs, and realistic what-if capacity/trade-off behavior. It also updated the pre-demo validation checklist and reconciled the Reethu/task-board documentation.

Reported results:
- Focused P8 integration suite: **19 passed, 0 failed**.
- Full suite at the P8 merge point: **231 passed, 0 failed**.
- Two pre-existing Starlette/AnyIO Python 3.14 environment deprecation warnings were noted.
- No backend or frontend production code was modified by P8.

## Current release-gate responsibility
The next QA step is integrated-system sign-off, not another feature:
1. Validate the real Deepansha dashboard against the live FastAPI backend.
2. Verify Normal/Peak/Surge demo flow without mock data in the final path.
3. Verify forecast, baseline, optimized allocation, waiting time, overload/backlog, improvement, explanation, and what-if values are real and internally consistent.
4. Re-run the full suite after dashboard/API integration changes.
5. Perform clean-clone setup and demo execution.
6. Rehearse the final demo and record exact failures as blocker/P0/P1/cosmetic.

## Critical rules
- Do not weaken tests to make the suite green.
- Do not accept fabricated or cherry-picked demo metrics.
- Treat simulation/optimization edge cases as P0 validation concerns.
- Flag API/data-contract drift immediately.
- Final sign-off requires reproducibility and actual evidence.

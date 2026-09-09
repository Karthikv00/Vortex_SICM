# Execution PRD — Reethu

## Responsibility
QA, data/scenario validation, demo validation, integration verification, documentation support.

## Deliverables
- `REETHU-001` Test scaffolding + strategy execution.
- `REETHU-002` Edge-case and scenario validation suite.
- `REETHU-003` Demo scenario validation and realism check.
- `REETHU-004` Documentation drift monitoring.

## Interfaces depended on
Every module's public function signatures; tests are contract-driven using `data-model.md` and `api-contract.md`.

## Interfaces provided
The test suite and `testing/validation-checklist.md` as the gate for demo polish.

## Acceptance criteria
All test cases pass or have documented justified exceptions; validation checklist complete before P9.

## Critical rules
Treat simulation edge cases as non-negotiable P0. Reject cherry-picked or fabricated demo improvement. Flag code/docs drift proactively.

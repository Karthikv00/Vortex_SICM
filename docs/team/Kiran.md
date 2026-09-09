# Execution PRD — Kiran

## Responsibility
Optimization, decision logic, explainability, and backend/API integration hardening.

## Completed deliverables
- `KIRAN-001` Optimization sizing benchmark + scoring validation. *(Completed & merged — PR #4)*
- `KIRAN-002` End-to-end deterministic DecisionPipeline integration. *(Completed & merged — PR #16)*
- `KIRAN-003` API + DecisionPipeline integration hardening. *(Completed & merged — PR #20)*
- `KIRAN-004` Baseline allocation, comparison, explanation, and what-if behavior. *(Completed & merged; explanation-weight alignment merged via PR #14.)*

## KIRAN-003 implementation outcome
The FastAPI optimization surface now exercises the real decision pipeline rather than a duplicated route-level flow. The integration validates the request → forecast → DecisionPipeline → serialization path and preserves the documented API error behavior.

Key outcomes:
- `POST /api/optimize` is wired through `DecisionPipeline`.
- Caller-supplied forecast remains supported while forecast generation can be performed by the pipeline path.
- `OptimizationResult` carries the forecast needed by the integrated consumer.
- Structured 422 validation is preserved for invalid inputs.
- Global/forecast internal failures return safe structured 500 responses without leaking exception details.
- API integration tests cover Normal/Peak/Surge execution, deterministic repeatability, baseline-vs-optimized response structure, invalid scenarios, and safe internal-error handling.
- PR #20 validation: `tests/test_api.py` 40/40 passed; related pipeline/optimization tests 71/71 passed; full suite at that point 220/220 passed; `git diff --check` clean.

## Current integrated state
The backend is no longer in feature-development mode. Karthi's latest integration/performance validation reports **231/231 tests passed**, Normal/Peak/Surge end-to-end success, 15/15 determinism checks, hard-constraint compliance, real-simulator optimizer validation, and average end-to-end runtimes of 13.7 ms (Normal), 16.5 ms (Peak), and 32.0 ms (Surge). No confirmed backend defect required a code change.

Reethu's pre-demo integration suite (PR #19) is also merged and covers the live API demo flow, determinism, API-boundary error handling, performance SLAs, and what-if tradeoffs.

## Current responsibility
Support Deepansha's real API → dashboard integration and resolve only genuine contract/integration blockers. Do not add new backend features or change optimization/simulation/forecast algorithms unless a confirmed P0 integration defect requires it and the team reviews the change.

## Critical rules
- Hard resource constraints must always be enforced.
- Explanations must be generated from actual computed metrics.
- Optimization claims must be validated against the real simulator.
- Deterministic seeded behavior is mandatory.
- No fabricated/cherry-picked metrics, mock data in the final demo path, secrets, or real customer data.
- Keep API contracts synchronized with implementation.

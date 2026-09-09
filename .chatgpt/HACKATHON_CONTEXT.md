# AAVISHKARA-26 — ChatGPT Orchestration State

> **ChatGPT-only state.** This file is orchestration context, not coding instructions. Coding agents must follow the user's task, official event rules/problem statement, `AGENTS.md`, `AI_INSTRUCTIONS.md`, project docs, and existing code.

## 1. Event and compliance
- Hackathon: AAVISHKARA-26; problem **JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer**.
- Team: Kiran, Karthi, Reethu, Deepansha.
- Event schedule documented by the project: 2026-09-09 10:00 → 2026-09-10 14:00; development from 13:30; judging-version freeze 2026-09-10 07:00; presentation window 09:00–12:30.
- Official problem statement/rules have highest authority. AI-assisted development is permitted only within those rules; registered team members remain responsible for understanding and validating submitted code.
- Synthetic data only. No fabricated/cherry-picked metrics. No secrets/credentials. Final submission must be reproducible from a clean clone.
- Do not assume event-specific exceptions such as backup recordings or submission formats unless confirmed by the authoritative organizer rules.

## 2. Product
Vortex SICM is a deterministic bank-branch operations decision-support dashboard, not an autonomous agent and not merely a queue simulator.

Core loop:
`synthetic data → demand forecast → queue simulation → resource allocation → baseline comparison → explainable recommendation → what-if result`

P0 requires multiple queues, Normal/Peak/Surge, forecast, waiting metrics, constrained allocation, baseline comparison, overload detection, explainable recommendation, what-if, and a clear dashboard.

## 3. Technical source of truth
- Backend/source-of-truth logic: Python + FastAPI.
- Core forecasting, simulation, optimization, constraints, and KPIs must work deterministically without an LLM.
- Frontend visualizes backend results; it must not duplicate business logic.
- Keep scope narrow: no auth/RBAC, microservices, real bank integrations, complex infrastructure, deep-learning-heavy forecasting, or autonomous agents before P0 is stable.

## 4. Repository
Repo: `Kiran-official/Vortex_SICM`; default branch: `main`.

Latest main integration commit after the current docs-sync branch is based on: `6a18af086733636f410539a72b2ba8ea4fb65a46`.

The repository contains the planning pack, backend implementation, tests, and active frontend work.

## 5. Completed work
- PR #1 — shared planning/specification pack synced to GitHub.
- PR #3 — product purpose and AI governance clarified.
- PR #4 — KIRAN-001 optimization sizing benchmark/scoring validation; ADR-004 benchmark.
- PR #5 — KARTHI-001 deterministic synthetic data and Normal/Peak/Surge scenarios.
- PR #6 — REETHU-001 generator validation tests.
- PR #7 — KARTHI-002 domain model validation hardening.
- PR #8 — deterministic API/explanation validation and contract hardening.
- PR #9 — centralized API allocation validation.
- PR #10 — KARTHI-003 simulation validation hardening.
- PR #11 — REETHU-003 demo scenario validation.
- PR #13 — KARTHI-004 demand forecasting completion/hardening.
- PR #14 — explanation-weight alignment/regression coverage.
- PR #15 — REETHU-002 forecast/simulation edge-case validation.
- PR #16 — KIRAN-002 transport-independent DecisionPipeline/domain validation.
- PR #17 — REETHU-004 documentation/code-drift reconciliation.
- PR #18 — KARTHI-005 safe FastAPI error handling.
- PR #19 — REETHU-P8 pre-demo end-to-end integration validation and checklist.
- PR #20 — KIRAN-003 API + DecisionPipeline integration hardening.

PR #12 was an earlier explanation-weight alignment attempt that was not merged; the intended change was completed through PR #14.

## 6. Latest validated state
### Karthi — KARTHI-006
Reported complete:
- 231/231 backend tests passed.
- Normal/Peak/Surge end-to-end pipelines verified.
- 15/15 determinism checks passed.
- Demand ordering verified.
- Hard staff constraints verified.
- Invalid queue IDs, negative staff/arrivals, incompatible forecasts, malformed scenarios, and infeasible allocations rejected.
- Optimized allocations validated through the real simulator.
- Five-run seed-42 average end-to-end runtime: 13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge.
- FastAPI/error-handling: 32/32 passed.
- No confirmed backend defect; no code changes required.

### Reethu — REETHU-P8
PR #19 merged. 19/19 focused integration tests and 231/231 full-suite tests passed at its merge point. Coverage includes live FastAPI demo flow, Normal/Peak/Surge, DecisionPipeline determinism, API-boundary errors, performance SLAs, and what-if trade-offs.

### Kiran — KIRAN-003
PR #20 merged. `POST /api/optimize` is wired through the real DecisionPipeline; forecast compatibility, structured 422 validation, safe 500 handling, Normal/Peak/Surge API integration, deterministic repeatability, and baseline-vs-optimized response structure are covered. Merge-point results: 40/40 API tests, 71/71 related pipeline/optimization tests, 220/220 full suite, clean `git diff --check`.

## 7. Team state
### Karthi
All implementation tasks KARTHI-001..006 are complete. Integration/performance support only unless a confirmed P0 defect appears.

### Kiran
KIRAN-001..004 are complete. Current role is integration support and API/decision-layer hardening only. Do not alter algorithms without evidence/team review.

### Reethu
REETHU-001..004 and P8 are complete. Current role is final integrated QA/release gate: dashboard validation, full regression, clean clone, demo rehearsal, metric traceability, and blocker classification.

### Deepansha
Dashboard work is the remaining primary implementation path. DEEPANSHA-003 is real FastAPI → dashboard integration and demo polish. No mock data in final/demo path.

## 8. Current remaining work
1. Deepansha: connect scenario controls to the real API; display real forecast, baseline/optimized metrics, overload/backlog/utilization, improvement, explanation/recommendation, and supported what-if; implement loading/error/empty/retry states.
2. Reethu: validate the integrated dashboard, rerun full tests, clean-clone setup, rehearse demo, and sign off release readiness.
3. Kiran/Karthi: support integration blockers only; avoid new backend features.

## 9. Demo
Intended story:
`normal → surge → forecast spike → overload → optimize → recommendation → measured before/after → explanation → what-if`

Existing real validation evidence includes 14.1% Normal wait reduction, 48.7% Peak wait reduction, and verified Surge capacity-expansion relief. Never hard-code or manually manufacture these or any other KPI.

## 10. Synchronization protocol
The repository is the implementation source of truth. Before substantive project actions, inspect current `main` and recent PRs when changes may have occurred. Update this file and relevant docs when project state changes. Do not assume old conversation context overrides GitHub state.

For task handoffs use: STARTED → READY FOR REVIEW → BLOCKED → INTEGRATION READY → DONE.

## 11. Decision discipline
Prefer the smallest complete, reproducible, explainable P0 system. Every change must preserve contracts, deterministic behavior, real measured evidence, and team ownership/compliance.

# AAVISHKARA-26 — ChatGPT Orchestration State

> **ChatGPT-only state.** This file is orchestration context, not coding instructions. Coding agents must follow the user's task, official event rules/problem statement, `AGENTS.md`, `AI_INSTRUCTIONS.md`, project docs, and existing code.

## 1. Event and compliance
- Hackathon: AAVISHKARA-26; problem **JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer**.
- Team: Kiran, Karthi, Reethu, Deepansha.
- Event schedule documented by the project: 2026-09-09 10:00 → 2026-09-10 14:00; development from 13:30; judging-version freeze 2026-09-10 07:00; presentation window 09:00–12:30.
- Official problem statement/rules have highest authority. AI-assisted development is permitted only within those rules; registered team members remain responsible for understanding and validating submitted code.
- Synthetic data only. No fabricated/cherry-picked metrics. No secrets/credentials. Final submission must be reproducible from a clean clone.

## 2. Product
Vortex SICM is a deterministic bank-branch operations decision-support dashboard, not an autonomous agent and not merely a queue simulator.

Core loop:
`synthetic data → demand forecast → queue simulation → resource allocation → baseline comparison → explainable recommendation → what-if result`

P0 requires multiple queues, Normal/Peak/Surge, forecast, waiting metrics, constrained allocation, baseline comparison, overload detection, explainable recommendation, what-if, and a clear dashboard.

## 3. Technical source of truth
- Backend/source-of-truth logic: Python + FastAPI.
- Forecasting, simulation, optimization, constraints, and KPIs must work deterministically without an LLM.
- Frontend visualizes backend results; it must not duplicate business logic.
- Keep scope narrow: no auth/RBAC, microservices, real bank integrations, complex infrastructure, deep-learning-heavy forecasting, or autonomous agents before P0 is stable.

## 4. Repository and current baseline
- Repo: `Kiran-official/Vortex_SICM`; default branch: `main`.
- Current `main`: `4c35a7a73909979e4e33d3521b6fca2cc92dbc35`, the PR #22 merge (`docs: refresh complete team state for dashboard integration`).
- Dashboard branch: `DEEPANSHA-001-dashboard`; not merged and currently has no PR.
- GitHub comparison at the latest check: dashboard branch is **7 commits ahead and 30 commits behind `main`**.
- This documentation reconciliation is being prepared on `docs/final-team-state-sync`; it does not directly change `main` until reviewed/merged.

## 5. Completed work history
- PR #1 — shared planning/specification pack synced to GitHub.
- PR #3 — product purpose, AI governance, and competition guardrails clarified.
- PR #4 — KIRAN-001 optimization sizing benchmark/scoring validation; ADR-004 evidence.
- PR #5 — KARTHI-001 deterministic synthetic data and Normal/Peak/Surge scenarios.
- PR #6 — REETHU-001 generator validation tests.
- PR #7 — KARTHI-002 domain model validation hardening.
- PR #8 — deterministic API/explanation validation and contract hardening.
- PR #9 — centralized API allocation validation.
- PR #10 — KARTHI-003 simulation validation hardening.
- PR #11 — REETHU-003 demo scenario realism and validation.
- PR #13 — KARTHI-004 demand forecasting completion/hardening.
- PR #14 — explanation-weight alignment/regression coverage.
- PR #15 — REETHU-002 forecast/simulation edge-case validation.
- PR #16 — KIRAN-002 transport-independent DecisionPipeline/domain validation.
- PR #17 — REETHU-004 documentation/code-drift reconciliation.
- PR #18 — KARTHI-005 safe FastAPI error handling.
- PR #19 — REETHU-P8 pre-demo end-to-end integration validation and checklist.
- PR #20 — KIRAN-003 API + DecisionPipeline integration hardening.
- PR #21 — consolidated project-state documentation synchronization.
- PR #22 — refreshed complete team state for dashboard integration.
- PR #12 was an earlier explanation-weight alignment attempt and was not merged; the intended change was completed through PR #14.

## 6. Team completion state
### Karthi — KARTHI-001..006 complete
Synthetic data, domain models, simulation, forecasting, API/error hardening, and integration/performance validation are complete. Latest reported evidence: **231/231 backend tests**, **15/15** determinism checks, seed-42 demand ordering Normal 213.00 < Peak 359.00 < Surge 874.17, hard constraints, invalid-input/infeasibility rejection, real-simulator optimization validation, and five-run seed-42 average runtimes of 13.7/16.5/32.0 ms for Normal/Peak/Surge (max 34.5 ms). FastAPI/error handling: **32/32**. No confirmed backend defect required a KARTHI-006 production code change.

### Kiran — KIRAN-001..004 complete
Optimization benchmark/scoring, transport-independent DecisionPipeline, real API integration, baseline/comparison/explanation/what-if behavior, and explainability alignment are complete. `POST /api/optimize` uses the real DecisionPipeline with structured 422 validation and safe structured 500 handling. Current role: integration support and genuine P0 blocker resolution only.

### Reethu — REETHU-001..004 + P8 complete
Generator QA, 34 forecast/simulation edge-case tests, demo scenario validation, documentation/code-drift reconciliation, and P8 are complete. P8: **19/19** focused integration tests and **231/231** full suite at merge. Current task: **REETHU-005 Final QA + Acceptance Validation**.

### Deepansha — DEEPANSHA-001..003 implemented on feature branch
Dashboard shell, full nine-section dashboard, UI states, and real FastAPI integration/demo polish are implemented on `DEEPANSHA-001-dashboard`. Reported verification: Vite build **48 modules**; live health/scenario/forecast/simulate/optimize/what-if HTTP flows; Normal/Peak/Surge live flows; structured 422 handling; backend-unavailable `ErrorState`; custom API integration checks. Playwright browser download failed due to external CDN 404; manual browser validation remains required.

The branch contains `frontend/src/mocks/mockData.js`. Its presence does not establish that mocks are used in production/demo execution, but the final/demo path must be explicitly verified as live-API-only.

## 7. Latest validated backend evidence
- Full backend regression: **231/231 passed**.
- Normal/Peak/Surge end-to-end pipelines verified.
- **15/15** repeated scenario+seed determinism checks passed.
- Seed-42 demand totals: Normal **213.00**, Peak **359.00**, Surge **874.17**.
- Optimized allocations satisfy queue min/max and total staff budget.
- Invalid queue IDs, negative staff/arrivals, incompatible forecasts, malformed scenarios, and infeasible allocations are rejected.
- Optimized allocations were verified through the real simulator.
- Seed-42 five-run average runtime: **13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge**; max **34.5 ms**.
- FastAPI/error handling: **32/32 passed**.
- Existing decision-quality evidence: Normal **14.1% wait reduction**, Peak **48.7% wait reduction**, Surge capacity-expansion relief.

## 8. Canonical seed-42 scenario evidence
- Normal: optimized `{teller:4, loans:1, customer_service:2}`; 211 served, 0 backlog; branch wait/p95 0/0.
- Peak: optimized `{teller:4, loans:2, customer_service:3}`; 362 served, 0 backlog; branch wait/p95 0/0.
- Surge: baseline and optimized `{teller:4, loans:3, customer_service:3}`; branch avg wait 93.6552 min, p95 153.8674 min, 25 overloaded slots, 730 served, 153 backlog. Baseline is globally optimal under the current objective/constraints.
- Surge what-if `{teller:5, loans:2, customer_service:3}`: avg wait 76.7 min; served 752.

## 9. Current remaining work
1. Deepansha: synchronize/rebase the dashboard branch with current main, open/review the dashboard PR, verify live-API-only final/demo paths, and polish only as needed.
2. Reethu: final integrated browser QA, metric traceability, full regression after dashboard merge, clean-clone validation, demo rehearsal, blocker classification, and sign-off.
3. Kiran/Karthi: integration support only; no new backend features unless a confirmed P0 blocker appears.

## 10. Release gates
Automated backend/API validation is green. Final release is **not signed off**. Remaining gates: dashboard synchronization and reviewed merge, browser validation, console/network cleanliness, loading/empty/error/retry verification, backend-to-UI metric traceability, full regression, clean-clone setup/test/demo, at least two rehearsals, final freeze, and organizer-specific rule confirmation.

## 11. Synchronization protocol
The repository is the implementation source of truth. Before substantive actions, inspect current `main`, branch divergence, and recent PRs when changes may have occurred. Update this file and relevant docs when project state changes. Do not let old conversation context override current GitHub state.

For task handoffs use: STARTED → READY FOR REVIEW → BLOCKED → INTEGRATION READY → DONE.

## 12. Decision discipline
Prefer the smallest complete, reproducible, explainable P0 system. Every change must preserve contracts, deterministic behavior, real measured evidence, and team ownership/compliance.

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
- Core forecasting, simulation, optimization, constraints, and KPIs must work deterministically without an LLM.
- Frontend visualizes backend results; it must not duplicate business logic.
- Keep scope narrow: no auth/RBAC, microservices, real bank integrations, complex infrastructure, deep-learning-heavy forecasting, or autonomous agents before P0 is stable.

## 4. Repository and current baseline
- Repo: `Kiran-official/Vortex_SICM`; default branch: `main`.
- Main's last consolidated documentation baseline before this update is PR #21 / merge commit `ad87af1`.
- This documentation update is being prepared on branch `docs/team-state-2026-09-09`; it records the latest team state without directly changing `main`.
- Deepansha's dashboard remains on `DEEPANSHA-001-dashboard` and is not yet merged into `main`.

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
- PR #12 was an earlier explanation-weight alignment attempt and was not merged; the intended change was completed through PR #14.

## 6. Team completion state
### Karthi — KARTHI-001..006 complete
Karthi completed synthetic data, domain models, simulation, forecasting, API/error hardening, and integrated performance validation. Latest reported evidence: **231/231 backend tests**, 15/15 determinism checks, demand ordering, hard constraints, real-simulator optimizer validation, and 13.7/16.5/32.0 ms average end-to-end runtimes for Normal/Peak/Surge. No confirmed backend defect required a code change for KARTHI-006.

### Kiran — KIRAN-001..004 complete
Kiran completed optimization benchmark/scoring, transport-independent DecisionPipeline, real API integration, baseline/comparison/explanation/what-if behavior, and explainability alignment. `POST /api/optimize` now uses the real DecisionPipeline with structured 422 validation and safe structured 500 handling.

### Reethu — REETHU-001..004 + P8 complete
Reethu completed generator QA, 34 forecast/simulation edge-case tests, demo scenario validation, documentation/code-drift reconciliation, and P8 with 19 end-to-end integration tests. Current task is **REETHU-005 Final QA + Acceptance Validation**.

### Deepansha — dashboard implementation on feature branch
Deepansha implemented DEEPANSHA-001 dashboard shell, DEEPANSHA-002 full dashboard, and DEEPANSHA-003 real FastAPI integration/demo polish on `DEEPANSHA-001-dashboard`. Integration evidence includes a 48-module Vite production build, real health/scenario/forecast/simulate/optimize/what-if HTTP flows through the Vite proxy, Normal/Peak/Surge live flows, structured 422 handling, backend-unavailable `ErrorState`, and custom API checks. Playwright browser download failed with an external CDN 404, which is a tooling limitation rather than a confirmed app defect.

The dashboard branch compares as **7 commits ahead and 19 commits behind `main`** and still needs PR/review/integration.

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

## 8. Canonical seed-42 scenario evidence
- Normal: baseline `{teller:4, loans:3, customer_service:3}` → optimized `{teller:4, loans:1, customer_service:2}`; 211 served, 0 backlog; branch wait/p95 0/0.
- Peak: baseline `{teller:4, loans:3, customer_service:3}` → optimized `{teller:4, loans:2, customer_service:3}`; 362 served, 0 backlog; branch wait/p95 0/0.
- Surge: baseline and optimized `{teller:4, loans:3, customer_service:3}`; branch avg wait 93.6552 min, p95 153.8674 min, 25 overloaded slots, 730 served, 153 backlog. Baseline is globally optimal under the current objective/constraints.
- Existing decision-quality evidence: Normal **14.1% wait reduction**, Peak **48.7% wait reduction**, Surge capacity-expansion relief.

## 9. Current remaining work
1. Deepansha: open/review dashboard PR, synchronize with latest main while preserving WIP, remove any remaining mock/hard-coded final-demo paths, and polish.
2. Reethu: final integrated browser QA, metric traceability, full regression after dashboard integration, clean-clone validation, demo rehearsal, blocker classification, and sign-off.
3. Kiran/Karthi: integration support only; no new backend features unless a confirmed P0 blocker appears.

## 10. Release gates
Automated backend/API validation is green. Final release is **not yet signed off**. Remaining gates: reviewed dashboard merge, real browser dashboard validation, console/network cleanliness, loading/empty/error/retry verification, backend-to-UI metric traceability, full regression, clean-clone setup/test/demo, at least two rehearsals, final freeze, and organizer-specific rule confirmation.

## 11. Synchronization protocol
The repository is the implementation source of truth. Before substantive actions, inspect current `main` and recent PRs when changes may have occurred. Update this file and relevant docs when project state changes. Do not let old conversation context override current GitHub state.

For task handoffs use: STARTED → READY FOR REVIEW → BLOCKED → INTEGRATION READY → DONE.

## 12. Decision discipline
Prefer the smallest complete, reproducible, explainable P0 system. Every change must preserve contracts, deterministic behavior, real measured evidence, and team ownership/compliance.

# AAVISHKARA-26 — ChatGPT Orchestration State

> **ChatGPT-only state.** This file is orchestration context, not coding instructions. Coding agents must follow the user's task, official event rules/problem statement, `AGENTS.md`, `AI_INSTRUCTIONS.md`, project docs, and existing code.

## 1. Event and compliance
- Hackathon: AAVISHKARA-26; problem **JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer**.
- Team: Kiran, Karthi, Reethu, Deepansha.
- Project-documented schedule: development from 2026-09-09 13:30; judging-version freeze 2026-09-10 07:00; presentation window 09:00–12:30.
- Official problem statement/rules have highest authority. AI-assisted development is permitted only within those rules; registered team members remain responsible for understanding and validating submitted code.
- Synthetic data only. No fabricated/cherry-picked metrics. No secrets/credentials. Final submission must be reproducible from a clean clone.
- Do not assume event-specific exceptions such as backup recordings or submission formats unless confirmed by authoritative organizer rules.

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

## 4. Repository
Repo: `Kiran-official/Vortex_SICM`; default branch: `main`.

Latest known `main`: `98d7d2458f50942dd4d751fb717685aa66af4a1a` — `docs: record final QA release-gate status`.

A documentation synchronization branch `docs/final-team-state-sync-20260909` is being prepared from that main state to record the latest Deepansha frontend integration and final team coordination state. No application behavior is being changed by that documentation work.

## 5. Completed GitHub work
- PR #1 — shared planning/specification pack synced.
- PR #3 — product purpose and AI governance clarified.
- PR #4 — KIRAN-001 optimization sizing benchmark/scoring validation + ADR-004.
- PR #5 — KARTHI-001 deterministic synthetic data + Normal/Peak/Surge.
- PR #6 — REETHU-001 generator validation tests.
- PR #7 — KARTHI-002 domain model validation hardening.
- PR #8 — deterministic API/explanation validation and contract hardening.
- PR #9 — centralized API allocation validation.
- PR #10 — KARTHI-003 simulation validation hardening.
- PR #11 — REETHU-003 demo scenario validation.
- PR #13 — KARTHI-004 demand forecasting completion/hardening.
- PR #14 — explanation-weight alignment/regression coverage; PR #12 was the earlier unmerged attempt.
- PR #15 — REETHU-002 forecast/simulation edge-case validation.
- PR #16 — KIRAN-002 transport-independent DecisionPipeline/domain validation.
- PR #17 — REETHU-004 documentation/code-drift reconciliation.
- PR #18 — KARTHI-005 safe FastAPI error handling.
- PR #19 — REETHU-P8 pre-demo end-to-end integration validation and checklist.
- PR #20 — KIRAN-003 API + DecisionPipeline integration hardening.
- PR #21 — consolidated documentation/project-state synchronization.
- Post-PR #21 — validation checklist refreshed with final QA release-gate status.

## 6. Karthi state — KARTHI-001..006 complete
Karthi owns synthetic data, domain models, demand forecasting, deterministic queue simulation, and backend/API support.

KARTHI-006 validation evidence:
- Full backend regression: **231/231 passed**.
- Normal/Peak/Surge end-to-end pipelines verified.
- Determinism: **15/15 scenario+seed checks passed**.
- Demand ordering: **Normal < Peak < Surge**.
- Optimized allocations satisfy hard staff constraints.
- Invalid queue IDs, negative staff/arrivals, incompatible forecasts, malformed scenarios, and infeasible allocations are rejected.
- Optimized allocations validated through the real simulator.
- Five-run seed-42 average end-to-end runtime: **13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge**.
- FastAPI/error-handling: **32/32 passed**.
- No confirmed backend defect; no production code change required.
- Final local working tree was clean and `main` synchronized with `origin/main`.

Current Karthi role: integration support only unless a confirmed P0 blocker appears.

## 7. Kiran state — KIRAN-001..004 complete
Kiran owns optimization, decision logic, baseline/comparison, explanation, what-if, and API integration support.

KIRAN-003 / PR #20:
- `POST /api/optimize` exercises the real `DecisionPipeline`.
- Caller-supplied forecast remains supported.
- Structured 422 validation preserved.
- Safe structured 500 responses prevent internal exception leakage.
- Normal/Peak/Surge API integration and deterministic repeatability validated.
- Baseline-vs-optimized response structure validated.
- Merge-point results: 40/40 API tests, 71/71 related pipeline/optimization tests, 220/220 full suite, clean `git diff --check`.

Current Kiran role: integration support and defect resolution only; no algorithm changes without evidence/team review.

## 8. Reethu state — REETHU-001..004 + P8 complete; REETHU-005 active
Reethu owns QA, scenario realism, regression protection, integration validation, and release readiness.

REETHU-P8 / PR #19:
- 19/19 focused integration tests passed.
- 231/231 full suite passed at merge point.
- Covered live FastAPI demo flow, Normal/Peak/Surge, DecisionPipeline determinism, malformed/invalid API payloads, performance SLAs, and what-if trade-offs.

Current REETHU-005 release gate:
- Validate the real dashboard against FastAPI.
- Cross-check frontend-visible metrics against backend responses.
- Verify browser console/network behavior and all UI states manually.
- Re-run full regression after dashboard merge.
- Perform clean-clone setup/test/demo.
- Rehearse at least twice and classify blockers/P0/P1/cosmetic issues.
- Sign off only after reproducibility is established.

## 9. Deepansha state — DEEPANSHA-001..003 implemented on feature branch
Deepansha owns dashboard shell, UX, visualization, UI states, and real backend integration.

Feature branch: `DEEPANSHA-001-dashboard`.
- `DEEPANSHA-001` dashboard shell/visualization foundation complete; initial UI commit `b033f45`.
- `DEEPANSHA-002` full dashboard implementation complete on the feature branch, including required sections and loading/empty/error states.
- `DEEPANSHA-003` real FastAPI integration implemented and pushed as `7609a8c`; **not yet merged into `main`**.

Verified frontend integration:
- `/api/scenario/generate` unwraps `{scenario, arrivals}` to canonical `ScenarioConfig`.
- `/api/simulate` and `/api/whatif` send `scenario + forecast + allocation`.
- `/api/optimize` synchronizes dashboard baseline/allocation/result from backend output.
- Live API mode is enabled by default.
- Real API errors surface instead of silently falling back to mocks.
- Backend remains source of truth for simulation/optimization.
- Vite production build passed with **48 modules transformed**.
- Real HTTP flows verified through Vite proxy + FastAPI for health, scenario, forecast, simulate, optimize, and what-if.
- Normal/Peak/Surge live flows verified.
- Invalid scenario, unknown queue, and over-capacity staff inputs returned structured 422 responses.
- Backend-unavailable behavior surfaced through `ErrorState`.
- Custom API integration verification passed.
- Playwright browser automation was attempted but browser download failed due to an external CDN **404**; this is a tooling limitation, not a confirmed application failure.

Measured live examples:
- Normal: 213 arrivals; 0 overloaded slots; 0.0 min average wait; optimized `{teller:4, loans:1, customer_service:2}`.
- Peak: 359 arrivals; 0 overloaded slots; 0.0 min average wait; optimized `{teller:4, loans:2, customer_service:3}`.
- Surge: 874 arrivals; baseline 93.7 min average wait, 153.9 min p95, 25 overloaded slots, 730 served. What-if `{teller:5, loans:2, customer_service:3}` reduced average wait to 76.7 min and increased served customers to 752.

These values are evidence from the real system and must never be hard-coded into the dashboard.

## 10. Current remaining work
1. Deepansha: open PR from `DEEPANSHA-001-dashboard` to `main`, obtain review, and preserve live API-only demo behavior.
2. Reethu: perform final integrated browser/dashboard QA, metric traceability, full regression after frontend merge, clean-clone validation, demo rehearsal, and release sign-off.
3. Kiran/Karthi: support integration blockers only; no new backend features unless a confirmed P0 integration defect blocks release.

## 11. Release gates
Automated backend/API validation is green. Final release sign-off remains open until:
- dashboard PR is reviewed and merged;
- manual browser validation is complete;
- browser console/network behavior is clean;
- loading/empty/error/retry states are manually verified;
- clean-clone setup/test/demo succeeds;
- final demo is rehearsed at least twice;
- final submitted version is frozen and matches the rehearsed/presented version;
- organizer-specific submission/presentation requirements are confirmed from authoritative event rules.

## 12. Demo
Intended story:
`normal → surge → forecast spike → overload → optimize → recommendation → measured before/after → explanation → what-if`

Existing deterministic decision-quality evidence includes 14.1% Normal wait reduction, 48.7% Peak wait reduction, and verified Surge capacity-expansion relief. All final KPIs must be generated dynamically by the real system.

## 13. Synchronization protocol
The repository is the implementation source of truth. Before substantive actions, inspect current `main` and recent PRs. Update this file and relevant docs when project state changes. Do not let old conversation context override current GitHub state.

Task handoff protocol: `STARTED → READY FOR REVIEW → BLOCKED → INTEGRATION READY → DONE`.

## 14. Decision discipline
Prefer the smallest complete, reproducible, explainable P0 system. Preserve contracts, deterministic behavior, real measured evidence, team ownership, and event compliance.

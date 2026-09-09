# Task Board

Use task IDs in commits and Slack `[CHANGE]` posts. Ownership is a responsibility boundary; integration work is coordinated across the team.

## Karthi — backend/data/simulation
- **KARTHI-001:** Synthetic data generator — deterministic normal/peak/surge. *(Completed & merged — PR #5)*
- **KARTHI-002:** Core domain models and validation. *(Completed & merged — PR #7)*
- **KARTHI-003:** Deterministic 15-minute-slot simulation and validation hardening. *(Completed & merged — PR #10)*
- **KARTHI-004:** Demand forecasting; deterministic rolling-average forecast with generator-owned scenario scaling. *(Completed & merged — PR #13)*
- **KARTHI-005:** FastAPI endpoint/error-handling hardening. *(Completed & merged — PR #18; API validation also hardened in PR #9)*
- **KARTHI-006:** Backend integration + performance validation. *(Completed — 231/231 tests, deterministic multi-seed validation, real-simulator optimizer validation, performance benchmarks; no code changes required.)*

## Kiran — optimization/decision/API integration
- **KIRAN-001:** Optimization sizing benchmark + scoring validation; real implementation counts/runtime and ADR-004 benchmark. *(Completed & merged — PR #4)*
- **KIRAN-002:** End-to-end deterministic DecisionPipeline, transport-independent domain validation, and integration. *(Completed & merged — PR #16)*
- **KIRAN-003:** API + DecisionPipeline integration hardening; real `/api/optimize` pipeline path, structured 422 validation, safe 500 behavior, and integration tests. *(Completed & merged — PR #20)*
- **KIRAN-004:** Baseline strategy, comparison, explanation, and what-if behavior are implemented and validated as part of the optimization stack. *(Completed & merged; explanation alignment completed in PR #14.)*

## Reethu — QA/validation
- **REETHU-001:** Generator validation scaffolding. *(Completed & merged — PR #6)*
- **REETHU-002:** Forecast/simulation edge-case validation suite. *(Completed & merged — PR #15)*
- **REETHU-003:** Demo scenario realism and deterministic validation. *(Completed & merged — PR #11; explanation alignment in PR #14)*
- **REETHU-004:** Documentation/code-drift reconciliation. *(Completed & merged — PR #17)*
- **REETHU-P8:** Pre-demo end-to-end integration validation and validation-checklist update. *(Completed & merged — PR #19)*
- **REETHU-005:** Final integrated QA, browser/dashboard validation, clean-clone validation, demo rehearsal, and release sign-off. *(Next active priority.)*

## Deepansha — dashboard
- **DEEPANSHA-001:** Dashboard shell + mock API layer; all required sections and explicit loading/empty/error states. *(Completed on feature branch; initial UI commit `b033f45`.)*
- **DEEPANSHA-002:** Full dashboard per approved design, including loading/empty/error states. *(Completed as part of the dashboard implementation on `DEEPANSHA-001-dashboard`.)*
- **DEEPANSHA-003:** Real FastAPI integration + demo polish. *(Implemented and pushed as commit `7609a8c`; awaiting PR/reviewer integration.)*

## Integrated state — 2026-09-09
The backend P0 path is implemented and validated through the real API surface:

`synthetic data → forecast → simulation → baseline → optimization → comparison → explanation → API → validation`

Latest main includes the merged pre-demo validation work (PR #19) and API/DecisionPipeline integration hardening (PR #20). Backend validation is **231/231 tests passed**. Karthi reports Normal/Peak/Surge end-to-end validation, 15/15 determinism checks, hard-constraint validation, real-simulator optimizer validation, and average end-to-end runtimes of 13.7 ms (Normal), 16.5 ms (Peak), and 32.0 ms (Surge), with no confirmed backend defects.

Deepansha synchronized `DEEPANSHA-001-dashboard` with latest `origin/main` by stashing WIP, merging `origin/main` cleanly, and restoring the stash. The branch then contained only the intended dashboard integration changes plus the local untracked scratch folder `skillset-dashboard/`.

Frontend validation completed:
- Production build passes with Vite 5.4.21: 48 modules transformed; output generated successfully.
- Real API integration verified through the Vite proxy and FastAPI for health, scenario generation, forecast, simulation, optimize, and what-if.
- Normal/Peak/Surge live API flows verified.
- Invalid scenario, unknown queue, and over-capacity staff inputs returned structured 422 errors.
- Backend-unavailable state surfaced through the dashboard ErrorState instead of silently falling back to mocks.
- Custom API integration verification passed.
- Playwright browser verification was attempted but could not download its browser because the external CDN returned 404; this is a tooling limitation, not an application failure.

Observed live verification examples from the real backend:
- NORMAL: 213 arrivals; baseline 0 overloaded slots and 0.0 min average wait; optimized allocation `{teller:4, loans:1, customer_service:2}`.
- PEAK: 359 arrivals; baseline 0 overloaded slots and 0.0 min average wait; optimized allocation `{teller:4, loans:2, customer_service:3}`.
- SURGE: 874 arrivals; baseline 93.7 min average wait, 153.9 min p95 wait, 25 overloaded slots, 730 served; what-if `{teller:5, loans:2, customer_service:3}` reduced average wait to 76.7 min and increased served customers to 752.

## Current priorities
1. **Deepansha:** open PR from `DEEPANSHA-001-dashboard` to `main` for review; do not merge before teammate/reviewer approval.
2. **Reethu:** final integrated QA, browser/dashboard validation, clean-clone validation, demo rehearsal, and release sign-off.
3. **Kiran/Karthi:** integration support only; no new backend features unless a confirmed integration defect blocks P0.

## Definition of done for current phase
- Real backend response drives the dashboard.
- Normal/Peak/Surge demo path works without code/data injection.
- Metrics are produced by deterministic backend computation and are traceable to simulation/optimization results.
- API errors are structured and safe; internal exception details are not exposed.
- Full backend test suite remains green.
- Clean clone can install, run, test, and execute the demo path.
- No secrets, real customer data, fabricated metrics, or unapproved scope are present.

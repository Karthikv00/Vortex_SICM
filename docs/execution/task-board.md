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
- **REETHU-005:** Final QA + acceptance validation: browser/dashboard verification, clean-clone validation, full regression, demo rehearsal, metric traceability, blocker classification, and release sign-off. *(Current release-gate responsibility)*

## Deepansha — dashboard
- **DEEPANSHA-001:** Dashboard shell and visualization structure. *(Active integration work)*
- **DEEPANSHA-002:** Full dashboard per approved design, including loading/empty/error states. *(Active integration work)*
- **DEEPANSHA-003:** Real FastAPI integration + demo polish. *(Current primary implementation priority; must consume real backend responses and remove final mock/demo data paths.)*

## Integrated state — 2026-09-09
The backend P0 path is implemented and validated through the real API surface:

`synthetic data → forecast → simulation → baseline → optimization → comparison → explanation → API → validation`

Latest merged documentation synchronization is PR #21, merge commit `ad87af1`. The latest reported backend validation is **231/231 tests passed**. Karthi reports Normal/Peak/Surge end-to-end validation, 15/15 determinism checks, hard-constraint validation, real-simulator optimizer validation, and average end-to-end runtimes of 13.7 ms (Normal), 16.5 ms (Peak), and 32.0 ms (Surge), with no confirmed backend defects.

## Current priorities
1. **Deepansha:** complete real API → dashboard integration and remove mock data from the final/demo execution path.
2. **Reethu:** final integrated QA, browser/dashboard validation, clean-clone validation, demo rehearsal, and release sign-off.
3. **Kiran/Karthi:** integration support only; do not introduce new backend features unless a confirmed integration defect blocks P0.

## Definition of done for the current phase
- Real backend response drives the dashboard.
- Normal/Peak/Surge demo path works without code/data injection.
- Metrics are produced by the deterministic system and are traceable to simulation/optimization results.
- API errors are structured and safe; internal exception details are not exposed.
- Full test suite remains green.
- Clean clone can install, run, test, and execute the demo path.
- No secrets, real customer data, fabricated metrics, or unapproved scope are present.

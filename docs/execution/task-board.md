# Task Board

Use task IDs in commits and Slack `[CHANGE]` posts. Ownership is a responsibility boundary; integration work is coordinated across the team.

## Karthi — backend/data/simulation
- **KARTHI-001:** Synthetic data generator — deterministic Normal/Peak/Surge. *(Completed & merged — PR #5)*
- **KARTHI-002:** Core domain models and validation. *(Completed & merged — PR #7)*
- **KARTHI-003:** Deterministic 15-minute-slot simulation and validation hardening. *(Completed & merged — PR #10)*
- **KARTHI-004:** Demand forecasting; deterministic rolling-average forecast with generator-owned scenario/time-of-day scaling. `_FORECAST_MULTIPLIERS` intentionally remains `1.0` to avoid double-counting. *(Completed & merged — PR #13)*
- **KARTHI-005:** FastAPI endpoint/error-handling hardening; safe structured 500 responses and server-side internal logging. *(Completed & merged — PR #18; API allocation validation also centralized in PR #9)*
- **KARTHI-006:** Backend integration + performance validation. *(Completed; no production code changes required.)*

### Karthi validation evidence
- Latest reported full backend regression: **231/231 passed**.
- Normal/Peak/Surge complete pipelines verified.
- Determinism: **15/15 scenario+seed checks passed**.
- Demand ordering: **Normal 213.00 < Peak 359.00 < Surge 874.17** for seed 42.
- Optimized allocations satisfy queue min/max and total staff budget.
- Invalid queue IDs, negative staff/arrivals, incompatible forecasts, malformed scenarios, and infeasible allocations are rejected.
- Optimized allocations were evaluated through the real simulator.
- Five-run seed-42 average end-to-end runtime: **13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge**; maximum observed runtime **34.5 ms**.
- FastAPI/error-handling suite: **32/32 passed**.

## Kiran — optimization/decision/API integration
- **KIRAN-001:** Optimization sizing benchmark + scoring validation; real implementation counts/runtime and ADR-004 evidence. *(Completed & merged — PR #4)*
- **KIRAN-002:** Transport-independent deterministic `DecisionPipeline`, domain forecast validation, and end-to-end integration. *(Completed & merged — PR #16)*
- **KIRAN-003:** API + DecisionPipeline integration hardening; real `/api/optimize` pipeline path, optional caller forecast, structured 422 validation, safe 500 behavior, and integration tests. *(Completed & merged — PR #20)*
- **KIRAN-004:** Baseline allocation, comparison, explanation, and what-if behavior; explanation-weight alignment completed through PR #14. *(Completed & merged)*

### Kiran validation evidence
- PR #20 merge-point: **40/40 API tests**, **71/71 related pipeline/optimization tests**, **220/220 full suite**, `git diff --check` clean.
- `POST /api/optimize` uses the real `DecisionPipeline` rather than duplicated route logic.
- Caller-supplied forecasts remain supported and are validated against the scenario.
- Optimization result carries the forecast required by the integrated consumer.
- Explanations are generated from actual computed metrics and allocation changes.

## Reethu — QA/validation
- **REETHU-001:** Generator validation scaffolding. *(Completed & merged — PR #6)*
- **REETHU-002:** Forecast/simulation edge-case validation suite: 34 dedicated tests. *(Completed & merged — PR #15)*
- **REETHU-003:** Demo scenario realism and deterministic validation. *(Completed & merged — PR #11; explanation alignment in PR #14)*
- **REETHU-004:** Documentation/code-drift reconciliation. *(Completed & merged — PR #17)*
- **REETHU-P8:** Pre-demo end-to-end integration validation and checklist update. *(Completed & merged — PR #19)*
- **REETHU-005:** Final QA + acceptance validation: browser/dashboard verification, clean-clone validation, full regression, demo rehearsal, metric traceability, blocker classification, and release sign-off. *(Current release-gate responsibility)*

### Reethu validation evidence
- REETHU-001: **22/22** focused tests; **91/91** full suite at merge point.
- REETHU-002: **34/34** focused edge-case tests; coverage includes determinism, horizons, invalid inputs, simulation invariants, overload/utilization, serialization, zero-staff behavior, and monotonicity.
- REETHU-P8: **19/19** focused end-to-end integration tests; **231/231** full suite at merge point.
- P8 covers live FastAPI demo flow, Normal/Peak/Surge, DecisionPipeline determinism, API-boundary invalid payloads, performance SLAs, and realistic what-if trade-offs.
- No production backend/frontend behavior was changed by P8.

## Deepansha — dashboard/UX/UI
- **DEEPANSHA-001:** Dashboard shell and visualization structure. *(Implemented on `DEEPANSHA-001-dashboard`; initial UI commit `b033f45`.)*
- **DEEPANSHA-002:** Full dashboard per approved design, including all required sections and loading/empty/error states. *(Implemented on `DEEPANSHA-001-dashboard`.)*
- **DEEPANSHA-003:** Real FastAPI integration + demo polish. *(Implemented on `DEEPANSHA-001-dashboard`; commit `7609a8c`.)*

### Deepansha current branch evidence
- Current GitHub comparison: **7 commits ahead and 30 commits behind `main`**. No PR currently exists for the branch.
- Branch includes Vite/React frontend, layout/header/sidebar, branch overview, metrics, queue cards, forecast/forecast chart, overload alerts, baseline/optimized allocation panels, comparison matrix, explanation panel, what-if simulator, loading/empty/error states, API service, and Vite proxy configuration.
- Vite production build verified with **48 modules**.
- Real HTTP flows were checked through Vite proxy + FastAPI for health, scenario generation, forecast, simulate, optimize, and what-if.
- Normal/Peak/Surge live flows and structured 422 behavior were checked.
- Backend-unavailable behavior reaches the dashboard `ErrorState`.
- Playwright automation was attempted, but browser download failed with an external CDN 404; manual browser validation is still required.
- `frontend/src/mocks/mockData.js` exists on the feature branch. This does not by itself establish that mocks are used in production/demo execution, but the final/demo path must be verified as live-API-only.
- Local `skillset-dashboard/` is scratch/untracked material and is not part of the intended task commit.
- **Next action:** synchronize/rebase the branch with current `main`, open the PR, review it, then hand over to Reethu for final integrated QA.

## Integrated state — 2026-09-09
The backend P0 path is implemented and validated through the real API surface:

`synthetic data → forecast → simulation → baseline → optimization → comparison → explanation → API → dashboard`

Current `main` is `4c35a7a73909979e4e33d3521b6fca2cc92dbc35`, the PR #22 documentation-state merge. The dashboard branch remains unmerged.

## P0 decision-quality evidence
Existing deterministic demo validation reports:
- **Normal:** 14.1% wait reduction.
- **Peak:** 48.7% wait reduction.
- **Surge:** capacity-expansion relief verified.

Seed-42 optimized allocations: Normal `{teller:4, loans:1, customer_service:2}`, Peak `{teller:4, loans:2, customer_service:3}`, Surge baseline/optimized `{teller:4, loans:3, customer_service:3}`.

## Current priorities
1. **Deepansha:** synchronize/rebase dashboard branch, open/review PR, verify no mock/demo execution path remains, and polish the demo.
2. **Reethu:** perform final integrated QA, browser verification, metric traceability, clean-clone validation, demo rehearsal, and release sign-off.
3. **Kiran/Karthi:** integration support only; no new backend feature work unless a confirmed P0 blocker appears.

## Definition of done for the current release phase
- Real FastAPI responses drive the final dashboard.
- Normal/Peak/Surge demo path works without code/data injection.
- Forecast, simulation, optimization, comparison, explanation, and what-if values are traceable to actual backend calculations.
- API errors are structured and safe; internal exception details are not exposed.
- Full regression remains green.
- Browser console/network behavior is clean enough for the demo.
- Loading/empty/error/retry states are verified.
- Clean clone can install, run, test, and execute the demo path.
- Demo is rehearsed at least twice.
- No secrets, real customer data, fabricated/cherry-picked metrics, or unapproved scope is present.

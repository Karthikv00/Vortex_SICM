# Validation Checklist (pre-demo)

## Backend and API validation
- [x] All currently defined backend/integration tests pass at the latest reported validation point: **231/231**.
- [x] Normal / Peak / Surge end-to-end pipelines verified.
- [x] Deterministic behavior verified across repeated/multiple seeded scenarios: **15/15 checks passed** in KARTHI-006.
- [x] Demand ordering verified: Normal < Peak < Surge where expected by the current contracts/tests.
- [x] Optimized allocations satisfy hard staff/resource constraints.
- [x] Optimized allocations validated through the real simulator.
- [x] Invalid queue IDs, negative staff/arrivals, incompatible forecasts, malformed scenarios, and infeasible allocations are rejected.
- [x] FastAPI/error-handling validation: **32/32 passed** in KARTHI-006.
- [x] KIRAN-003 API integration validated: `tests/test_api.py` **40/40**, related pipeline/optimization tests **71/71**, full suite at merge point **220/220**.
- [x] Safe 500 responses do not expose internal exception details.
- [x] `git diff --check` clean on the KIRAN-003 validation.
- [x] REETHU-P8 end-to-end integration suite: **19/19 passed**.

## Performance and decision-quality validation
- [x] Seed-42 average end-to-end runtime measured by Karthi: **13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge** (5 runs each).
- [x] Maximum observed canonical runtime was **34.5 ms**.
- [x] Optimization remains within the documented `<3 s` P0 target for intended MVP sizing.
- [x] Demo seed produces real, measurable improvement from the deterministic system: Normal **14.1%** wait reduction; Peak **48.7%** wait reduction; Surge capacity-expansion relief verified.
- [x] Explanation output is traceable to computed metrics and allocation changes.
- [x] What-if behavior is validated through genuine backend calculations; P8 reported `<1.5 s` SLA compliance.

## Dashboard branch validation evidence
- [x] Deepansha dashboard shell and full nine-section dashboard are implemented on `DEEPANSHA-001-dashboard`.
- [x] Vite production build verified with **48 modules**.
- [x] Real HTTP flows verified through Vite proxy + FastAPI for health, scenario generation, forecast, simulate, optimize, and what-if.
- [x] Normal / Peak / Surge live flows verified on the dashboard branch.
- [x] Structured 422 behavior for invalid inputs verified.
- [x] Backend-unavailable path reaches the dashboard `ErrorState`.
- [x] Custom API integration checks completed.
- [ ] Dashboard branch reviewed and merged into `main`.
- [ ] Playwright browser automation completed. *(Previous attempt was blocked by external CDN browser-download 404; manual browser validation is still required.)*

## Dashboard/rehearsal release gate
- [ ] No frontend console errors during the full real-backend demo.
- [ ] Loading/empty/error states manually verified in the browser.
- [ ] All final dashboard data paths use live FastAPI responses; no mock data remains in the demo path.
- [ ] Scenario selector works for Normal / Peak / Surge against the real backend.
- [ ] Dashboard shows forecast, baseline vs optimized results, waiting/overload/backlog/utilization metrics, improvement, recommendation/explanation, and supported what-if results.
- [ ] Frontend-visible metrics are cross-checked against actual backend responses.
- [ ] Full demo rehearsed at least twice, preferably by two different people.
- [ ] Clean-clone setup and demo path verified.

## Release/compliance gate
- [x] Synthetic data only.
- [x] Deterministic seeded behavior preserved.
- [x] No fabricated or cherry-picked metrics used as evidence.
- [x] No known backend defect remains from the latest integration validation.
- [ ] Final submitted version is frozen and matches the rehearsed/presented version.
- [ ] Official event-specific submission/presentation requirements have been checked against the authoritative organizer rules.

## Current release status
Backend/API automated validation is complete and green. Deepansha's dashboard implementation and real API integration are validated on the feature branch but are **not yet merged into the release baseline**. The final release gate remains **OPEN** until dashboard review/merge, browser verification, metric traceability, clean-clone validation, rehearsal, and final freeze are evidenced. Do not claim final QA sign-off before those checks are complete.

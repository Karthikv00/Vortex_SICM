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
- [x] Optimization remains within the documented `<3 s` P0 target for intended MVP sizing.
- [x] Demo seed produces real, measurable improvement from the deterministic system (existing validation evidence: Normal **14.1%** wait reduction; Peak **48.7%** wait reduction; Surge capacity-expansion relief verified).
- [x] Explanation output is traceable to computed metrics and allocation changes.
- [x] What-if behavior is validated through genuine backend calculations; P8 reported `<1.5 s` SLA compliance.

## Dashboard integration evidence
- [x] Deepansha Vite production build passed: **48 modules transformed**.
- [x] Real HTTP flows verified through Vite proxy + FastAPI for health, scenario generation, forecast, simulate, optimize, and what-if.
- [x] Normal / Peak / Surge live API flows verified.
- [x] Invalid scenario, unknown queue, and over-capacity staff inputs returned structured **422** responses.
- [x] Backend-unavailable behavior surfaced through the dashboard `ErrorState`.
- [x] Custom API integration verification passed.
- [ ] Final dashboard integration PR reviewed and merged into `main`.

## Dashboard/rehearsal release gate
- [ ] No frontend console errors during the full real-backend demo.
- [ ] Loading/empty/error/retry states manually verified in the browser.
- [ ] All final dashboard data paths use live FastAPI responses; no mock data remains in the demo path.
- [ ] Scenario selector works for Normal / Peak / Surge against the real backend.
- [ ] Dashboard shows forecast, baseline vs optimized results, waiting/overload/backlog/utilization metrics, improvement, recommendation/explanation, and supported what-if results.
- [ ] Frontend-visible metrics are cross-checked against actual backend responses during the final browser run.
- [ ] Full demo rehearsed at least twice, preferably by two different people.
- [ ] Clean-clone setup and demo path verified.
- [ ] Backup demo path prepared only if permitted by the official event rules.

## Tooling limitation
Playwright browser automation was attempted for the integrated dashboard, but the external browser-download CDN returned **404**. This is a tooling limitation rather than a confirmed application failure. Manual browser verification remains mandatory.

## Release/compliance gate
- [x] Synthetic data only.
- [x] Deterministic seeded behavior preserved.
- [x] No fabricated or cherry-picked metrics used as evidence.
- [x] No known backend defect remains from the latest integration validation.
- [ ] Final submitted version is frozen and matches the rehearsed/presented version.
- [ ] Official event-specific submission/presentation requirements have been checked against the authoritative organizer rules.

## Current release status
Backend/API automated validation is complete and green. Deepansha's real dashboard/API implementation is ready for PR/review on `DEEPANSHA-001-dashboard`. The final release gate remains **OPEN** until merge, manual browser validation, clean-clone validation, and rehearsal are evidenced.

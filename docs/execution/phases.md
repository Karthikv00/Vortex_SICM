# Phase Plan

Timeline: development started 2026-09-09 13:30; judging-version freeze is documented as 2026-09-10 07:00. The project has now moved from component implementation into integration, release validation, and demo readiness.

## P0 — Repository + architecture lock
**Complete.** Shared planning/specification pack, engineering rules, AI/compliance guardrails, architecture, contracts, task board, testing, design, demo, and participant execution PRDs are in the repository.

## P1 — Core data + domain model
**Complete.** Karthi delivered deterministic synthetic data and strengthened domain validation. Reethu added aligned generator validation coverage.

## P2 — Simulation engine
**Complete.** Karthi delivered the deterministic 15-minute-slot simulation and hardened negative-arrival, invalid-slot, and zero-staff overload behavior. Reethu validated edge cases.

## P3 — Demand prediction
**Complete.** KARTHI-004 delivered deterministic rolling-average forecasting while keeping scenario/time-of-day scaling centralized in the data generator to avoid double-counting.

## P4 — Optimization + baseline comparison
**Complete.** Kiran's optimizer uses feasible-allocation enumeration, hard constraints, deterministic scoring/tie-breaking, baseline comparison, explanation, and what-if behavior. Optimization was validated against the real simulator.

## P5 — API
**Complete.** FastAPI routes and validation/error handling are integrated. `POST /api/optimize` exercises the real `DecisionPipeline`; structured 422 responses and safe structured 500 responses are covered.

## P6 — Dashboard
**Complete on Deepansha's feature branch.** Dashboard shell, visualization structure, required sections, and loading/empty/error states are implemented.

## P7 — End-to-end integration
**Implemented on Deepansha's feature branch; merge pending.** Real FastAPI integration is pushed as `7609a8c`. Vite proxy + FastAPI flows for health, scenario, forecast, simulate, optimize, and what-if have been verified across Normal/Peak/Surge. Real API errors surface instead of silently falling back to mocks.

## P8 — Testing + bug fixing
**Backend/API complete.** Reethu-P8 merged 19 end-to-end integration tests; Karthi-006 added final backend integration/performance validation. Latest full backend regression is 231/231 passed.

## P9 — Demo polish + final integrated QA
**Current phase.** Deepansha needs PR/review/merge and manual browser verification. Reethu owns final QA, metric traceability, clean-clone validation, and rehearsal. Kiran/Karthi provide integration support only.

## P10 — Submission freeze
**Pending.** Freeze the exact version that has passed integrated QA and rehearsal. Confirm organizer-specific submission/presentation rules from the authoritative event source before final submission.

## Current evidence
- Full backend regression: **231/231 passed**.
- Determinism: **15/15 scenario+seed checks passed**.
- Demand ordering: **Normal < Peak < Surge**.
- Optimized allocations satisfy hard staff constraints and are evaluated through the real simulator.
- Five-run seed-42 average end-to-end runtime: **13.7 ms Normal, 16.5 ms Peak, 32.0 ms Surge**.
- FastAPI/error handling: **32/32 passed** in KARTHI-006 validation.
- Deepansha Vite production build: **48 modules transformed successfully**.
- Playwright browser automation was blocked by an external browser-download **404**; manual browser verification remains required.

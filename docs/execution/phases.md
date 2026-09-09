# Phase Plan

Timeline: development starts 2026-09-09 13:30; judging-version freeze 2026-09-10 07:00. Compress P0–P7 into the first ~10–12 hours and preserve time for P8–P10. If simulation is not stable within the first ~4 hours, escalate immediately because it is the critical path.

## P0 — Repository + architecture lock
All four read PRD, TRD, and their own execution PRD.

## P1 — Core data + domain model
Karthi leads generator/models; Kiran reviews; Reethu tests; Deepansha works in parallel on dashboard shell + mocks. Exit: deterministic normal/peak/surge generation and contract models pass tests.

## P2 — Simulation engine
Karthi owns; Kiran supports constraints; Reethu edge-case tests. Exit: simulation test cases pass. Kiran may prototype optimizer against a stub in parallel.

## P3 — Demand prediction
Karthi or Kiran. Deterministic forecast covers full horizon with no missing slots. Runs alongside P2.

## P4 — Optimization + baseline comparison
Kiran owns; Karthi integrates simulation; Reethu validates feasibility. Exit: optimization correct on normal/peak/surge and infeasible case handled.

## P5 — API
Karthi owns FastAPI; Kiran supports optimize/what-if. Exit: all documented endpoints implemented and contract-tested.

## P6 — Dashboard
Deepansha owns; Reethu supports UX/demo validation. All 9 sections and loading/empty/error states implemented, initially with mocks.

## P7 — End-to-end integration
Deepansha + Karthi. Switch frontend from mocks to real API and run the demo flow live.

## P8 — Testing + bug fixing
Reethu leads; all hands fix defects.

## P9 — Demo polish
Reethu + Kiran narrative; Deepansha visual polish.

## P10 — Submission freeze
Kiran owns; all four verify.

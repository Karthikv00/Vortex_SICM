# Dashboard Specification

Single-page layout following demo narrative order.

1. **Branch overview:** branch name, operating hours, total staff, scenario selector (`normal`/`peak`/`surge`).
2. **Current queues:** queue name, current staff, current average wait, near/over-threshold cue.
3. **Demand forecast:** expected arrivals per queue over the horizon; highlight surge window.
4. **Overload alerts:** explicit overloaded slots and queues from simulation.
5. **Baseline allocation:** staff count per queue plus average wait, p95 wait, utilization.
6. **Optimized allocation:** same shape as baseline, with visible staff deltas.
7. **Before/after metrics:** average wait, p95 wait, overloaded slot count side by side; this is the primary measurable-improvement panel.
8. **What-if controls:** per-queue staff adjustment and re-simulation; show resulting metrics.
9. **Explanation panel:** plain-language `explanation`, optionally expandable score breakdown.

## Required states
Every data-driven panel has explicit loading, empty, and error states. Errors use the structured API error format and retry where sensible.

## Interactions
- Scenario change refetches forecast, re-runs baseline simulation, and clears stale optimized/what-if results.
- Optimize calls `/api/optimize` and populates sections 6–9.
- What-if changes are debounced to `/api/whatif` and update only the what-if section.

## Required real metrics
Average wait, p95 wait, utilization %, and overloaded slot count must always be real computed values, never placeholders.

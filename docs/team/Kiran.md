# Execution PRD — Kiran

## Responsibility
Optimization and product/AI direction, decision logic, explainability, and backend integration support.

## Deliverables
- `KIRAN-001` Optimization sizing benchmark + scoring validation.
- `KIRAN-002` Enumeration/scoring/tie-break optimizer.
- `KIRAN-003` Deterministic explanation generation.
- `KIRAN-004` Baseline allocation strategy + what-if logic.

## Current repository state
The current `main` branch already contains implementations for `KIRAN-002`, `KIRAN-003`, and `KIRAN-004` under `backend/optimization/`, plus optimization tests under `tests/test_optimization.py`.

These implementations must not be treated as fully complete merely because the files exist. Their next gate is measured validation against the current real simulation engine and the official performance/acceptance requirements.

## Immediate next task — KIRAN-001

**Goal:** benchmark and validate the existing optimization path using the real implementation.

### Do this next
1. Pull/re-read current `main` before editing.
2. Run the existing optimization tests and record the exact result.
3. Run the real optimizer against deterministic normal, peak, and surge scenarios.
4. Measure:
   - number of feasible allocations evaluated
   - optimizer runtime
   - representative simulation runtime
   - baseline score
   - optimized score
   - average wait before/after
   - p95 wait before/after
   - overloaded slots before/after
   - any end-of-horizon backlog difference
5. Verify hard constraints for the selected allocation.
6. Verify deterministic output across repeated runs.
7. Check whether the current optimizer satisfies the documented `<3 second` optimization target for the intended MVP sizing.
8. Update `docs/decisions/ADR-004-optimization-strategy.md` with measured numbers and conclusion.
9. Fix only concrete defects discovered by the benchmark/tests; do not redesign the optimizer spec without evidence.

### Important
Do not fabricate or cherry-pick favorable metrics. Record actual measurements. If the environment prevents execution, report that verification was not performed.

## Interfaces depended on
`SimulationResult` from Karthi's simulation engine; `ScenarioConfig` and `ForecastResult` contracts.

## Interfaces provided
`optimize(scenario, forecast) -> OptimizationResult` and deterministic explanation generation used by the optimization result.

## Acceptance criteria
FR-OPT-1 through FR-OPT-5, FR-EXP-1/2, and FR-WHATIF baseline strategy requirements.

## Critical rules
- Do not treat optimizer results as correct until validated against the real simulation engine.
- Explanations must be generated from actual computed numbers.
- Benchmark enumeration against real implementation counts and keep the optimization path under the documented 3-second target for the intended MVP sizing.
- Hard resource constraints must always be enforced.

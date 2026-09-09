# Acceptance Criteria (P0)

## Data generation
- Same scenario + seed produces identical generated arrival data.
- `surge` has measurably higher arrival rates than `normal` in at least one window.

## Forecasting
- Forecast returns expected arrivals per queue per slot for the full horizon with no missing slots.

## Simulation
- Simulation returns average wait, p95 wait, utilization, and overload flags.
- Zero arrivals produces zero wait and no crash.
- Zero staff on an open queue reports full backup/infeasibility rather than silently ignoring it.

## Optimization
- Feasible allocations respect all hard constraints and optimized score is ≥ baseline score.
- Infeasible problems explicitly return no-feasible-allocation rather than a best-effort invalid result.
- Equal-score allocations use the documented deterministic tie-break.

## Explainability
- Explanation contains constraints, per-objective score breakdown, and a plain-language reason traceable to computed numbers.

## What-if
- Manual allocation uses the same simulation engine and units as optimizer output.

## API
- Malformed input produces 4xx with structured error information, not 500/stack trace.

## Dashboard
- Clicking optimize on the demo scenario populates recommendation, before/after comparison, and explanation from real computed data within the 2–3 second interaction target.

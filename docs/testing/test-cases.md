# Test Cases

## Data
- TC-01: Same seed + scenario → identical output.
- TC-02: Surge peak arrival rate > normal in at least one slot.
- TC-03: Generated data covers every horizon slot.

## Simulation
- TC-04: Normal + adequate staff → low/no overload; waits near service-time floor.
- TC-05: Peak + baseline staff → some overload expected.
- TC-06: Surge + baseline staff → significant overload expected.
- TC-07: Zero arrivals → wait 0, utilization 0, no crash.
- TC-08: Zero staff with arrivals → overloaded from first arrival, backlog grows monotonically, no crash.
- TC-09: Staff far above demand → utilization near 0, no divide-by-zero, no negative waits.

## Forecasting
- TC-10: Forecast slot count exactly matches scenario horizon.
- TC-11: Forecast values non-negative.

## Optimization
- TC-12: Feasible allocation respects all min/max and total-staff constraints.
- TC-13: Optimized objective score ≤ baseline score on same scenario (lower penalty is better).
- TC-14: Sum of queue minimums > available staff → `feasible: false`, no invalid allocation.
- TC-15: Exactly one feasible allocation → return it without error.
- TC-16: Equal scores → deterministic documented tie-break.
- TC-17: `total_staff_available == 0` → explicit infeasible result, no crash.

## What-if
- TC-18: Manual allocation returns SimulationResult with same units/shape as optimizer results.

## API
- TC-19: Malformed JSON → 4xx structured error.
- TC-20: Missing required field → 4xx naming field.
- TC-21: `/api/health` → 200 and `{"status":"ok"}`.

## End-to-end
- TC-22: Surge scenario optimization is feasible, respects all hard constraints, and does not regress score or p95 wait over baseline (baseline is optimal at 10 staff per ADR-004; what-if demonstrates capacity expansion).

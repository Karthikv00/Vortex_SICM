# Optimization Design

## Approach
Exhaustive enumeration of feasible allocations is appropriate at ≤6 queues and ≤20 staff. Filter hard constraints first; score each feasible allocation using one simulation run.

## Hard constraints
- `sum(staff_by_queue) <= total_staff_available`
- `min_staff[q] <= staff_by_queue[q] <= max_staff[q]`
- Open queues must have at least their configured minimum staff.

Invalid allocations are never scored or returned.

## Objective
`objective = w1*wait_score + w2*overload_score + w3*utilization_score + w4*reallocation_cost`

Default weights (updated after KIRAN-001 benchmark -- see ADR-004):
- wait: 0.4
- overload: 0.4
- utilization: 0.1
- reallocation cost: 0.1

Terms are normalized to comparable ranges. Wait combines branch-wide average and p95 wait (normalized to 400 min reference); overload uses overloaded-slot count (normalized to 32 slots); utilization rewards a target utilization band (0.6-0.85); reallocation cost is normalized total absolute staff movement from baseline (normalized to 20 staff).

## Tie-breaking
For equal scores within floating-point tolerance, prefer lower reallocation cost, then stable enumeration order. Must be deterministic.

## Benchmark requirement
`KIRAN-001` must benchmark real implementation counts and update ADR-004 with measured numbers. The binding optimization target is under 3 seconds at hackathon scale.

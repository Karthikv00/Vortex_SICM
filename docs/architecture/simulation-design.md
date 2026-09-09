# Simulation Design

## Approach: time-step simulation
Default slot width is 15 minutes. For each queue in each slot:
1. Add expected arrivals to backlog.
2. Available server-minutes = `staff_count * slot_minutes`.
3. Serve backlog up to available server-minutes using `avg_service_time_minutes` per customer.
4. Carry unserved backlog forward; it accrues wait.
5. Record customers served/waiting, wait time added, and utilization = server-minutes used / available server-minutes.

At horizon end, calculate per-queue and branch-wide average wait, p95 wait, mean utilization, and overloaded slots.

Default overload starting point: backlog > `2 × staff_count` customers; tune during P2/P4 based on realistic demo numbers.

## Determinism
All randomness is confined to seeded data generation. Given the same `ForecastResult` and `AllocationPlan`, simulation output is identical.

## Why not discrete-event simulation
Full per-customer event simulation is more complex and harder to make deterministic/explainable under hackathon time constraints. Time-step simulation is sufficient to demonstrate surge → overload → reallocation → improvement.

## Edge cases
- Zero arrivals: no backlog change and zero wait contribution.
- Zero staff on an open queue with arrivals: backlog grows and queue is overloaded from the first arrival slot; never silently skipped.
- Staff exceeding demand: utilization falls below 1 without divide-by-zero.

P1 extension: stochastic service-time distributions only if they clearly improve the demo without destabilizing the core engine.

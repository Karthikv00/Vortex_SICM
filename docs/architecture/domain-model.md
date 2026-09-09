# Domain Model

## Core entities

**Branch** — one branch per demo run; has service queues, total staff pool, and operating horizon.

**ServiceQueue** — one service type (Teller, Loans, Account Services, Customer Support). Fields: `queue_id`, `name`, `min_staff`, `max_staff`, `avg_service_time_minutes`.

**TimeSlot** — fixed-width interval (15 or 30 minutes) within the horizon; simulation, forecasting, and metrics are indexed by slot.

**Customer (synthetic)** — generated rather than persisted individually; fields `arrival_time`, `queue_id`, `service_time`.

**Staff** — allocatable capacity assigned to one queue for the scenario in P0; represented as an integer count per queue. Skill compatibility is deferred to P1.

**ScenarioConfig** — scenario name (`normal`/`peak`/`surge`), seed, horizon, arrival-rate profile per queue/slot.

**AllocationPlan** — mapping `queue_id -> staff_count`; comparisons use `baseline` and `optimized` or `whatif` instances.

**ForecastResult** — predicted arrivals per queue per slot.

**SimulationResult** — per-queue and branch-wide average wait, p95 wait, utilization, and overload flags.

**OptimizationResult** — baseline allocation/result, optimized allocation/result, score breakdown, and explanation.

## Relationships
- A Branch has many ServiceQueues.
- ScenarioConfig generates arrivals over TimeSlots.
- ForecastResult is derived from ScenarioConfig plus optional historical data.
- SimulationResult is derived from ForecastResult + AllocationPlan.
- OptimizationResult wraps baseline and optimized simulation results plus reasoning.

See `data-model.md` for field-level schemas and `api-contract.md` for API serialization.

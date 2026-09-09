# ADR-004: Optimization Strategy

**Status:** Accepted and validated. Exhaustive enumeration confirmed feasible for P0 scope.
Benchmarked: 2026-09-09 | Seed: 42 | Machine: Windows, Python 3.13.5

## Decision

Use exhaustive enumeration of feasible allocations, scored by the weighted objective in
`architecture/optimization-design.md`. No scipy, OR-Tools, or metaheuristics for P0.

## Objective Function (Final)

```
score = 0.4 * wait_score + 0.4 * overload_score + 0.1 * utilization_score + 0.1 * reallocation_cost
```

- **wait_score**: `min(1.0, (0.6 * avg_wait + 0.4 * p95_wait) / 400.0)`
- **overload_score**: `min(1.0, overloaded_slot_count / 32)`
- **utilization_score**: deviation from target band [0.60, 0.85]
- **reallocation_cost**: `min(1.0, total_staff_movement / 20.0)`

### Change History

Original weights were `wait=0.4, overload=0.3, util=0.2, realloc=0.1` with
`MAX_EXPECTED_WAIT_MINUTES=60`. The KIRAN-001 benchmark discovered a pathological
surge allocation (see "Surge Pathology Fix" below). Fix applied:
- `MAX_EXPECTED_WAIT_MINUTES`: 60 -> 400 (restores wait discrimination in surge)
- `W_OVERLOAD`: 0.3 -> 0.4 (overload is more important than utilization efficiency)
- `W_UTIL`: 0.2 -> 0.1 (reduces spurious tiebreaker effect)

## Sizing (Post-Fix Measurements -- Real Implementation, No Mocks)

All three scenarios share the same constraint space:
- 3 queues, 10 total staff, per-queue range [min, max]
- Product space (before filter): 72 combinations
- Feasible after constraint filter: 62 allocations

| Metric | Normal | Peak | Surge |
|---|---|---|---|
| Feasible allocations | 62 | 62 | 62 |
| Enum runtime | 0.000085s | 0.000032s | 0.000030s |
| Single sim runtime | 0.000579s | 0.000349s | 0.000894s |
| Full opt runtime | 0.019s | 0.025s | 0.046s |
| **P0 sim target (<1.0s)** | **PASS** | **PASS** | **PASS** |
| **P0 opt target (<3.0s)** | **PASS** | **PASS** | **PASS** |
| Baseline avg wait (min) | 0.0000 | 0.0000 | 93.66 |
| Optimized avg wait (min) | 0.0000 | 0.0000 | 93.66 |
| Baseline p95 wait (min) | 0.0000 | 0.0000 | 153.87 |
| Optimized p95 wait (min) | 0.0000 | 0.0000 | 153.87 |
| Baseline overloaded slots | 0 | 0 | 25 |
| Optimized overloaded slots | 0 | 0 | 25 |
| Baseline end backlog | 0 | 0 | 153 |
| Optimized end backlog | 0 | 0 | 153 |
| Baseline score | 0.048539 | 0.015317 | 0.505440 |
| Optimized score | 0.016906 | 0.006139 | 0.505440 |
| Selected allocation | teller:4, loans:1, cs:2 | teller:4, loans:2, cs:3 | teller:4, loans:3, cs:3 |
| Constraint valid | PASS | PASS | PASS |
| Deterministic | PASS | PASS | PASS |

## Surge Pathology Fix (KIRAN-001)

### Problem (Before Fix)
The original objective selected `teller:6, loans:2, cs:2` for surge, which:
- Reduced avg wait 93.66 -> 90.22 min (small improvement)
- **Increased p95 wait 153.87 -> 319.02 min** (2x worse)
- **Increased overloaded slots 25 -> 28** (worse)
- **Increased end backlog 153 -> 192** (worse)

### Root Cause
Two compounding issues:
1. `MAX_EXPECTED_WAIT_MINUTES=60` caused ALL surge allocations to score `wait_score=1.0`
   (surge waits range 72-853 min, all above 60), eliminating wait discrimination entirely.
2. With wait equalized, `utilization_score` (weight 0.2) became the dominant tiebreaker.
   The pathological allocation concentrated staff at teller, creating an artificially
   favorable average utilization (closer to the 0.6-0.85 target band) while worsening
   p95 wait and overload in the starved queues.

### Fix Applied
- Raised `MAX_EXPECTED_WAIT_MINUTES` from 60 to 400, covering the observed surge p95
  range (81-853 min). Normal/peak produce 0.0 wait and are unaffected by the cap value.
- Raised `W_OVERLOAD` from 0.3 to 0.4 to match the spec intent (overload > utilization).
- Lowered `W_UTIL` from 0.2 to 0.1 to reduce the distorting tiebreaker effect.
- Weights still sum to 1.0.

### Result (After Fix)
The optimizer now correctly identifies the baseline allocation as optimal for surge --
no feasible reallocation improves the objective without introducing p95/overload
regression. This is the correct behavior: with 10 staff and severe demand, no
staff redistribution helps. The pathological allocation is no longer selected.

## Validation Tests (63 total, all pass)

### test_benchmark_validation.py (31 tests, TC-BM-01 through TC-BM-12):
- Runtime targets per scenario (TC-BM-01, TC-BM-02)
- Hard constraint validity on selected allocation (TC-BM-03)
- Score monotonicity: optimized <= baseline (TC-BM-04)
- Allocation determinism (TC-BM-05)
- Explanation determinism -- elapsed_seconds defect fix verified (TC-BM-06, TC-BM-07)
- All enumerated allocations feasible (TC-BM-08)
- Surge p95 and overload regression guard (TC-BM-09)
- No exception on any scenario (TC-BM-10)
- Pathological allocation regression guard (TC-BM-11)
- Weights sum to 1.0 (TC-BM-12)

### test_optimization.py (7 tests, TC-12 through TC-22):
- TC-22 updated: asserts optimized score <= baseline + constraints valid (not
  avg_wait_reduction > 0, which was only satisfiable by the pathological allocation).

## Defect Found and Fixed -- Non-Deterministic Explanation

`explain.py` previously included `elapsed_seconds` (wall-clock runtime) in the
rendered explanation string. This made the explanation non-deterministic across runs.
Fixed by removing `elapsed_seconds` and replacing "evaluated in X.XXs" with
"evaluated exhaustively". Regression guards in TC-BM-06 and TC-BM-07.

## Rationale

Enumeration is deterministic, debuggable, and explainable. With 62 feasible allocations
and optimization completing in 19-46ms (far below 3s), there is no demonstrated need
for more sophisticated solvers at hackathon P0 scale.

## Consequence

Does not scale to very large branch networks (many queues, many staff). Revisit only
if future requirements materially exceed the 3-second P0 target.

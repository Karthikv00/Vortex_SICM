"""
backend/optimization/optimizer.py — Exhaustive feasible-allocation optimizer.

Approach (ADR-004):
  Enumerate all feasible staff allocations for ≤6 queues and ≤20 staff.
  Filter hard constraints first (no simulation cost for infeasible allocations).
  Score each feasible allocation with one real simulation run.
  Return the allocation with the best (lowest) objective score.

Hard constraints (never violated):
  - sum(staff_by_queue) <= total_staff_available
  - min_staff[q] <= staff_by_queue[q] <= max_staff[q] for every queue

Objective (lower is better):
  score = w_wait * wait_score
        + w_overload * overload_score
        + w_util * utilization_score
        + w_realloc * reallocation_cost

Weights (from optimization-design.md):
  wait: 0.4, overload: 0.3, utilization: 0.2, reallocation cost: 0.1

Tie-breaking:
  For equal scores (within TOLERANCE), prefer lower reallocation cost,
  then stable enumeration order. Fully deterministic.

Implements: KIRAN-001 (sizing/benchmark), KIRAN-002 (optimizer)
Spec:       docs/architecture/optimization-design.md
            docs/decisions/ADR-004-optimization-strategy.md
"""

from __future__ import annotations

import itertools
import logging
import time
from typing import Dict, List, Optional, Tuple

from backend.models import (
    AllocationPlan,
    AllocationWithResult,
    ForecastResult,
    ImprovementSummary,
    OptimizationResult,
    ScenarioConfig,
    ScoreBreakdown,
    SimulationResult,
)
from backend.optimization.baseline import InfeasibleBaselineError, baseline_allocation
from backend.simulation.engine import simulate

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Objective weights (from optimization-design.md — treat as spec, not tunable)
# ---------------------------------------------------------------------------
# W_WAIT=0.4, W_OVERLOAD=0.3, W_UTIL=0.2, W_REALLOC=0.1 were the original values.
# KIRAN-001 benchmark found the 60-min wait cap caused ALL surge allocations to
# score wait=1.0, making utilization the spurious tiebreaker. Fix:
#   W_OVERLOAD raised 0.3→0.4  (matches spec intent: overload > utilization)
#   W_UTIL    lowered 0.2→0.1  (reduces distorting effect of util when wait is saturated)
# Weights still sum to 1.0. See ADR-004 for benchmark evidence.
# ---------------------------------------------------------------------------
W_WAIT = 0.4
W_OVERLOAD = 0.4
W_UTIL = 0.1
W_REALLOC = 0.1

# Floating-point tolerance for tie-breaking equality
TOLERANCE = 1e-6

# Target utilization band (reward allocations that land in this range)
UTIL_TARGET_LOW = 0.60
UTIL_TARGET_HIGH = 0.85

# ---------------------------------------------------------------------------
# Normalization reference values (derived from surge scenario upper bounds)
# These keep score components in a comparable [0, 1] range.
# ---------------------------------------------------------------------------
# MAX_EXPECTED_WAIT_MINUTES was 60.0. KIRAN-001 benchmark showed surge waits
# reach 90–853 min, collapsing all surge allocations to wait_score=1.0 and
# eliminating wait discrimination. Raised to 400 to cover the full observed
# surge p95 range (81–853 min) while keeping normal/peak scores unchanged
# (they produce 0.0 wait and are unaffected by the cap). See ADR-004.
MAX_EXPECTED_WAIT_MINUTES = 400.0  # Raised from 60 — see ADR-004 KIRAN-001 fix
MAX_OVERLOAD_SLOTS = 32            # 09:00-17:00 / 15min = 32 slots maximum
MAX_REALLOC_COST = 20.0            # Max plausible absolute staff movement


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _score_wait(result: SimulationResult) -> float:
    """
    Normalized wait score. Combines average and p95 branch-wide wait.
    Lower is better. Capped at 1.0.
    """
    bw = result.branch_wide
    combined = 0.6 * bw.avg_wait_minutes + 0.4 * bw.p95_wait_minutes
    return min(1.0, combined / MAX_EXPECTED_WAIT_MINUTES)


def _score_overload(result: SimulationResult) -> float:
    """
    Normalized overload score. Fraction of horizon slots that are overloaded.
    Lower is better.
    """
    return min(1.0, result.branch_wide.overloaded_slot_count / MAX_OVERLOAD_SLOTS)


def _score_utilization(result: SimulationResult) -> float:
    """
    Utilization score. Penalises allocations outside the target band [0.6, 0.85].
    Within band → 0.0 (perfect). Outside → penalty proportional to deviation.
    Lower is better.
    """
    if not result.per_queue:
        return 0.0
    utils = [qr.utilization for qr in result.per_queue.values()]
    avg_util = sum(utils) / len(utils)
    if UTIL_TARGET_LOW <= avg_util <= UTIL_TARGET_HIGH:
        return 0.0
    elif avg_util < UTIL_TARGET_LOW:
        return (UTIL_TARGET_LOW - avg_util) / UTIL_TARGET_LOW
    else:
        return (avg_util - UTIL_TARGET_HIGH) / (1.0 - UTIL_TARGET_HIGH)


def _score_reallocation(
    candidate: AllocationPlan,
    baseline: AllocationPlan,
) -> float:
    """
    Normalized reallocation cost: total absolute staff movement from baseline.
    Lower is better.
    """
    total_movement = sum(
        abs(candidate.staff_by_queue.get(qid, 0) - baseline.staff_by_queue.get(qid, 0))
        for qid in candidate.staff_by_queue
    )
    return min(1.0, total_movement / MAX_REALLOC_COST)


def compute_score(
    result: SimulationResult,
    candidate: AllocationPlan,
    baseline: AllocationPlan,
) -> Tuple[float, ScoreBreakdown]:
    """
    Compute the weighted objective score for a candidate allocation.

    Returns (total_score, ScoreBreakdown). Lower total_score is better.
    """
    ws = _score_wait(result)
    os_ = _score_overload(result)
    us = _score_utilization(result)
    rc = _score_reallocation(candidate, baseline)

    total = W_WAIT * ws + W_OVERLOAD * os_ + W_UTIL * us + W_REALLOC * rc

    breakdown = ScoreBreakdown(
        wait_score=round(ws, 6),
        overload_score=round(os_, 6),
        utilization_score=round(us, 6),
        reallocation_cost=round(rc, 6),
        total_score=round(total, 6),
    )
    return total, breakdown


# ---------------------------------------------------------------------------
# Feasibility check
# ---------------------------------------------------------------------------

def is_feasible(
    staff_by_queue: Dict[str, int],
    scenario: ScenarioConfig,
) -> bool:
    """
    Return True iff staff_by_queue satisfies all hard constraints:
    - sum <= total_staff_available
    - min_staff[q] <= staff[q] <= max_staff[q] for each queue
    """
    total = sum(staff_by_queue.values())
    if total > scenario.total_staff_available:
        return False
    for q in scenario.queues:
        s = staff_by_queue.get(q.queue_id, 0)
        if s < q.min_staff or s > q.max_staff:
            return False
    return True


# ---------------------------------------------------------------------------
# Feasible allocation enumeration
# ---------------------------------------------------------------------------

def enumerate_feasible_allocations(scenario: ScenarioConfig) -> List[Dict[str, int]]:
    """
    Generate all feasible staff allocations as a list of dicts.

    Uses itertools.product over per-queue [min_staff, max_staff] ranges.
    Filters on total_staff constraint.

    At ≤6 queues and ≤20 staff the product space before filtering is
    manageable (typically low thousands); after filtering it is smaller.
    """
    queues = scenario.queues
    ranges = [range(q.min_staff, q.max_staff + 1) for q in queues]
    queue_ids = [q.queue_id for q in queues]

    feasible = []
    for combo in itertools.product(*ranges):
        total = sum(combo)
        if total <= scenario.total_staff_available:
            feasible.append(dict(zip(queue_ids, combo)))
    return feasible


# ---------------------------------------------------------------------------
# Main optimizer entry point
# ---------------------------------------------------------------------------

def optimize(
    scenario: ScenarioConfig,
    forecast_result: ForecastResult,
) -> OptimizationResult:
    """
    Find the best feasible staff allocation via exhaustive enumeration.

    Steps:
    1. Compute the baseline allocation and simulate it.
    2. Enumerate all feasible allocations.
    3. If none (infeasible scenario), return explicit infeasible result.
    4. Score each feasible allocation against the real simulation engine.
    5. Select best (lowest score); tie-break on reallocation cost then enum order.
    6. Return OptimizationResult with baseline, optimized, scores, improvement, explanation.

    Deterministic for a given (scenario, forecast).
    """
    t0 = time.perf_counter()

    # Build avg_service_times lookup from scenario
    avg_service_times: Dict[str, float] = {
        q.queue_id: q.avg_service_time_minutes for q in scenario.queues
    }

    # ----------------------------------------------------------------
    # 1. Baseline
    # ----------------------------------------------------------------
    try:
        base_plan = baseline_allocation(scenario)
    except InfeasibleBaselineError as e:
        # Scenario is fundamentally infeasible — report explicitly
        logger.warning("Infeasible scenario: %s", e)
        return _infeasible_result(scenario, forecast_result, avg_service_times, str(e))

    base_result = simulate(forecast_result, base_plan, avg_service_times, scenario.slot_minutes)
    base_score, _ = compute_score(base_result, base_plan, base_plan)

    # ----------------------------------------------------------------
    # 2. Enumerate feasible allocations
    # ----------------------------------------------------------------
    feasible_allocs = enumerate_feasible_allocations(scenario)
    n_feasible = len(feasible_allocs)
    logger.info(
        "Optimization: scenario=%s, feasible_allocations=%d", scenario.scenario_name, n_feasible
    )

    if n_feasible == 0:
        return _infeasible_result(
            scenario, forecast_result, avg_service_times,
            "No feasible allocation satisfies all queue min/max and total staff constraints."
        )

    # ----------------------------------------------------------------
    # 3. Score each feasible allocation
    # ----------------------------------------------------------------
    best_plan: Optional[Dict[str, int]] = None
    best_score = float("inf")
    best_result: Optional[SimulationResult] = None
    best_breakdown: Optional[ScoreBreakdown] = None
    best_realloc_cost: float = float("inf")

    for alloc_dict in feasible_allocs:
        candidate = AllocationPlan(label="optimized", staff_by_queue=alloc_dict)
        result = simulate(forecast_result, candidate, avg_service_times, scenario.slot_minutes)
        score, breakdown = compute_score(result, candidate, base_plan)

        realloc = breakdown.reallocation_cost

        # Tie-break: lower reallocation cost first, then stable enum order
        is_better = (
            score < best_score - TOLERANCE
            or (abs(score - best_score) <= TOLERANCE and realloc < best_realloc_cost - TOLERANCE)
        )
        if is_better:
            best_score = score
            best_plan = alloc_dict
            best_result = result
            best_breakdown = breakdown
            best_realloc_cost = realloc

    elapsed = time.perf_counter() - t0
    logger.info(
        "Optimization complete in %.3fs. Best score: %.6f (baseline: %.6f)",
        elapsed, best_score, base_score,
    )

    opt_plan = AllocationPlan(label="optimized", staff_by_queue=best_plan)

    # ----------------------------------------------------------------
    # 4. Improvement summary
    # ----------------------------------------------------------------
    improvement = ImprovementSummary(
        avg_wait_reduction_minutes=round(
            base_result.branch_wide.avg_wait_minutes - best_result.branch_wide.avg_wait_minutes, 4
        ),
        p95_wait_reduction_minutes=round(
            base_result.branch_wide.p95_wait_minutes - best_result.branch_wide.p95_wait_minutes, 4
        ),
        overloaded_slots_resolved=max(
            0,
            base_result.branch_wide.overloaded_slot_count
            - best_result.branch_wide.overloaded_slot_count,
        ),
        utilization_delta=round(
            _avg_utilization(best_result) - _avg_utilization(base_result), 4
        ),
    )

    # ----------------------------------------------------------------
    # 5. Explanation (deterministic — no LLM required)
    # ----------------------------------------------------------------
    from backend.optimization.explain import explain_result  # avoid circular import
    explanation = explain_result(
        scenario=scenario,
        base_plan=base_plan,
        opt_plan=opt_plan,
        base_result=base_result,
        opt_result=best_result,
        breakdown=best_breakdown,
        improvement=improvement,
        n_feasible=n_feasible,
    )

    return OptimizationResult(
        scenario_name=scenario.scenario_name,
        baseline=AllocationWithResult(allocation=base_plan, result=base_result, score=round(base_score, 6)),
        optimized=AllocationWithResult(allocation=opt_plan, result=best_result, score=round(best_score, 6)),
        score_breakdown=best_breakdown,
        improvement=improvement,
        explanation=explanation,
        feasible=True,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _avg_utilization(result: SimulationResult) -> float:
    if not result.per_queue:
        return 0.0
    vals = [q.utilization for q in result.per_queue.values()]
    return sum(vals) / len(vals)


def _infeasible_result(
    scenario: ScenarioConfig,
    forecast_result: ForecastResult,
    avg_service_times: Dict[str, float],
    reason: str,
) -> OptimizationResult:
    """
    Build an explicit infeasible OptimizationResult.

    Per FR-OPT-5 and data-model.md: feasible=False, optimized == baseline,
    explanation states why.
    """
    # Use an empty allocation (zero staff) as a placeholder when baseline can't be built
    zero_alloc = AllocationPlan(
        label="baseline",
        staff_by_queue={q.queue_id: 0 for q in scenario.queues},
    )
    zero_result = simulate(forecast_result, zero_alloc, avg_service_times, scenario.slot_minutes)
    zero_score, zero_breakdown = compute_score(zero_result, zero_alloc, zero_alloc)

    empty_improvement = ImprovementSummary(
        avg_wait_reduction_minutes=0.0,
        p95_wait_reduction_minutes=0.0,
        overloaded_slots_resolved=0,
        utilization_delta=0.0,
    )
    placeholder = AllocationWithResult(
        allocation=zero_alloc, result=zero_result, score=round(zero_score, 6)
    )

    return OptimizationResult(
        scenario_name=scenario.scenario_name,
        baseline=placeholder,
        optimized=placeholder,
        score_breakdown=zero_breakdown,
        improvement=empty_improvement,
        explanation=f"No feasible allocation found. Reason: {reason}",
        feasible=False,
    )

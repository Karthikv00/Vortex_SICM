"""
backend/optimization/explain.py — Deterministic explanation generation.

Generates a plain-language recommendation explanation traceable entirely
to computed numbers — no LLM required (FR-EXP-2).

An LLM may optionally rephrase this text for UX polish, but the deterministic
version is the authoritative explanation used in tests and the API.

Implements: KIRAN-003
Spec:       docs/requirements/functional-requirements.md FR-EXP-1/2
"""

from __future__ import annotations

from backend.models import (
    AllocationPlan,
    ImprovementSummary,
    ScenarioConfig,
    ScoreBreakdown,
    SimulationResult,
)


def explain_result(
    scenario: ScenarioConfig,
    base_plan: AllocationPlan,
    opt_plan: AllocationPlan,
    base_result: SimulationResult,
    opt_result: SimulationResult,
    breakdown: ScoreBreakdown,
    improvement: ImprovementSummary,
    n_feasible: int,
) -> str:
    """
    Generate a structured plain-language explanation of the optimization result.

    The explanation answers:
    1. What scenario was analyzed?
    2. What constraint was respected?
    3. What demand caused the recommendation?
    4. What changed between baseline and optimized?
    5. What measurable improvement was observed?
    6. Why was this allocation selected?

    All numbers come from actual computed simulation results — never fabricated.
    """
    lines: list[str] = []

    # ----------------------------------------------------------------
    # 1. Scenario context
    # ----------------------------------------------------------------
    scenario_label = scenario.scenario_name.upper()
    lines.append(
        f"Scenario: {scenario_label}. "
        f"Branch hours {scenario.horizon_start}–{scenario.horizon_end}, "
        f"{scenario.slot_minutes}-minute slots, "
        f"{scenario.total_staff_available} total staff available."
    )

    # ----------------------------------------------------------------
    # 2. Constraint summary
    # ----------------------------------------------------------------
    queue_constraints = ", ".join(
        f"{q.name}: min {q.min_staff}–max {q.max_staff}"
        for q in scenario.queues
    )
    lines.append(f"Hard constraints respected: {queue_constraints}.")

    # ----------------------------------------------------------------
    # 3. Baseline situation
    # ----------------------------------------------------------------
    base_alloc_str = ", ".join(
        f"{q.name}: {base_plan.staff_by_queue.get(q.queue_id, 0)} staff"
        for q in scenario.queues
    )
    lines.append(
        f"Baseline allocation ({base_alloc_str}) produced: "
        f"avg wait {base_result.branch_wide.avg_wait_minutes:.1f} min, "
        f"p95 wait {base_result.branch_wide.p95_wait_minutes:.1f} min, "
        f"{base_result.branch_wide.overloaded_slot_count} overloaded slot(s)."
    )

    # ----------------------------------------------------------------
    # 4. What was overloaded
    # ----------------------------------------------------------------
    overloaded_queues = [
        (q.name, qr.overloaded_slots)
        for q in scenario.queues
        for qid, qr in base_result.per_queue.items()
        if q.queue_id == qid and qr.overloaded_slots
    ]
    if overloaded_queues:
        overload_detail = "; ".join(
            f"{name} overloaded at {', '.join(slots[:3])}{'...' if len(slots) > 3 else ''}"
            for name, slots in overloaded_queues
        )
        lines.append(f"Overload detected: {overload_detail}.")
    else:
        lines.append("No overloaded slots under baseline allocation.")

    # ----------------------------------------------------------------
    # 5. Recommended allocation and staff movements
    # ----------------------------------------------------------------
    movements = []
    for q in scenario.queues:
        base_s = base_plan.staff_by_queue.get(q.queue_id, 0)
        opt_s = opt_plan.staff_by_queue.get(q.queue_id, 0)
        delta = opt_s - base_s
        if delta > 0:
            movements.append(f"+{delta} to {q.name} ({base_s}→{opt_s})")
        elif delta < 0:
            movements.append(f"{delta} from {q.name} ({base_s}→{opt_s})")

    opt_alloc_str = ", ".join(
        f"{q.name}: {opt_plan.staff_by_queue.get(q.queue_id, 0)}"
        for q in scenario.queues
    )
    if movements:
        lines.append(
            f"Recommended allocation: {opt_alloc_str}. "
            f"Staff movement: {', '.join(movements)}."
        )
    else:
        lines.append(
            f"Recommended allocation matches baseline: {opt_alloc_str}. "
            f"No staff movement needed — baseline is already optimal."
        )

    # ----------------------------------------------------------------
    # 6. Measured improvement
    # ----------------------------------------------------------------
    if improvement.avg_wait_reduction_minutes > 0 or improvement.overloaded_slots_resolved > 0:
        lines.append(
            f"Result: avg wait reduced by {improvement.avg_wait_reduction_minutes:.1f} min "
            f"({base_result.branch_wide.avg_wait_minutes:.1f} → "
            f"{opt_result.branch_wide.avg_wait_minutes:.1f} min); "
            f"p95 wait reduced by {improvement.p95_wait_reduction_minutes:.1f} min; "
            f"{improvement.overloaded_slots_resolved} overloaded slot(s) resolved."
        )
    else:
        lines.append(
            f"Result: optimized metrics equal or marginally better than baseline "
            f"(avg wait {opt_result.branch_wide.avg_wait_minutes:.1f} min, "
            f"p95 {opt_result.branch_wide.p95_wait_minutes:.1f} min)."
        )

    # ----------------------------------------------------------------
    # 7. Score breakdown and why selected
    # ----------------------------------------------------------------
    lines.append(
        f"Selection basis: lowest weighted objective score ({breakdown.total_score:.4f}) "
        f"from {n_feasible} feasible allocations evaluated exhaustively. "
        f"Score components -- wait: {breakdown.wait_score:.3f} (x0.4), "
        f"overload: {breakdown.overload_score:.3f} (x0.3), "
        f"utilization: {breakdown.utilization_score:.3f} (x0.2), "
        f"reallocation cost: {breakdown.reallocation_cost:.3f} (x0.1)."
    )

    return " ".join(lines)

"""
backend/resilience/recovery.py — Operational Recovery Plan Recommendations.

Generates and ranks least-disruptive feasible recovery interventions:
1. Optimal Staff Reallocation (budget-neutral, shifting capacity to bottleneck).
2. Minimal Disruption Quick Shift (single staff transfer from surplus queue).
3. Temporary Surge Float Staff (+1 reserve staff within queue bounds).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.models import (
    AllocationPlan,
    ForecastResult,
    ScenarioConfig,
    SimulationResult,
)
from backend.optimization.optimizer import (
    compute_score,
    enumerate_feasible_allocations,
    optimize,
)
from backend.simulation.engine import simulate


def _describe_staffing_changes(diff: Dict[str, int], queue_names: Dict[str, str]) -> str:
    """Generate concise human-readable description of staff movements."""
    donors = []
    recipients = []
    for qid, delta in diff.items():
        name = queue_names.get(qid, qid.replace("_", " ").title())
        if delta < 0:
            donors.append(f"{abs(delta)} {name}")
        elif delta > 0:
            recipients.append(f"{delta} {name}")

    if donors and recipients:
        return f"Move {', '.join(donors)} → {', '.join(recipients)}"
    elif recipients and not donors:
        return f"Deploy {', '.join(recipients)} (Surge Buffer)"
    elif donors and not recipients:
        return f"Stand down {', '.join(donors)}"
    return "Maintain current staff distribution"


def find_recovery_plans(
    scenario: ScenarioConfig,
    stressed_forecast: ForecastResult,
    stressed_result: SimulationResult,
    current_allocation: AllocationPlan,
    bottleneck_queue: str,
) -> List[Dict[str, Any]]:
    """
    Evaluate and rank feasible operational recovery plans for the stressed condition.
    """
    avg_service_times = {q.queue_id: q.avg_service_time_minutes for q in scenario.queues}
    queue_names = {q.queue_id: q.name for q in scenario.queues}
    baseline_wait = stressed_result.branch_wide.avg_wait_minutes
    baseline_overload = stressed_result.branch_wide.overloaded_slot_count

    plans: List[Dict[str, Any]] = []
    seen_allocations = set()

    # Base allocation signature
    curr_sig = tuple(sorted(current_allocation.staff_by_queue.items()))
    seen_allocations.add(curr_sig)

    # -----------------------------------------------------------------------
    # Plan 1: Optimal Staff Reallocation (Budget-Neutral)
    # -----------------------------------------------------------------------
    opt_res = optimize(scenario, stressed_forecast)
    if opt_res.feasible and opt_res.optimized:
        opt_alloc = opt_res.optimized.allocation.staff_by_queue
        sig = tuple(sorted(opt_alloc.items()))
        if sig not in seen_allocations:
            seen_allocations.add(sig)
            diff = {qid: opt_alloc.get(qid, 0) - current_allocation.staff_by_queue.get(qid, 0) for qid in opt_alloc}
            disruption = sum(abs(d) for d in diff.values())
            res = opt_res.optimized.result
            new_wait = res.branch_wide.avg_wait_minutes
            new_overload = res.branch_wide.overloaded_slot_count

            plans.append({
                "id": "plan-optimal-reallocation",
                "title": "Optimal Workforce Reallocation",
                "strategy": "reallocate",
                "action": _describe_staffing_changes(diff, queue_names),
                "resulting_allocation": opt_alloc,
                "staffing_change": diff,
                "average_wait_minutes": round(new_wait, 1),
                "overloaded_slots": new_overload,
                "wait_reduction_minutes": round(max(0.0, baseline_wait - new_wait), 1),
                "overload_reduction_count": max(0, baseline_overload - new_overload),
                "disruption_score": disruption,
                "feasibility": "Fully Feasible (Budget Neutral)",
                "staff_budget": scenario.total_staff_available,
            })

    # -----------------------------------------------------------------------
    # Plan 2: Minimal-Disruption Quick Shift
    # (Move exactly 1 employee from least loaded queue to bottleneck queue)
    # -----------------------------------------------------------------------
    q_utils = [
        (qid, qr.utilization, current_allocation.staff_by_queue.get(qid, 0))
        for qid, qr in stressed_result.per_queue.items()
        if qid != bottleneck_queue
    ]
    # Pick queue with lowest utilization and staff above min_staff
    candidate_donors = [
        (qid, util, staff)
        for qid, util, staff in sorted(q_utils, key=lambda x: x[1])
        if staff > scenario.queue_by_id(qid).min_staff
    ]

    target_queue_cfg = scenario.queue_by_id(bottleneck_queue)
    curr_target_staff = current_allocation.staff_by_queue.get(bottleneck_queue, 0)

    if candidate_donors and curr_target_staff < target_queue_cfg.max_staff:
        donor_qid, _, _ = candidate_donors[0]
        shift_alloc = dict(current_allocation.staff_by_queue)
        shift_alloc[donor_qid] -= 1
        shift_alloc[bottleneck_queue] += 1

        sig = tuple(sorted(shift_alloc.items()))
        if sig not in seen_allocations:
            seen_allocations.add(sig)
            plan_obj = AllocationPlan(label="whatif", staff_by_queue=shift_alloc)
            sim_res = simulate(stressed_forecast, plan_obj, avg_service_times, scenario.slot_minutes)
            new_wait = sim_res.branch_wide.avg_wait_minutes
            new_overload = sim_res.branch_wide.overloaded_slot_count
            diff = {qid: shift_alloc.get(qid, 0) - current_allocation.staff_by_queue.get(qid, 0) for qid in shift_alloc}

            plans.append({
                "id": "plan-quick-shift",
                "title": "Targeted Quick Shift (Single Transfer)",
                "strategy": "minimal_reallocation",
                "action": _describe_staffing_changes(diff, queue_names),
                "resulting_allocation": shift_alloc,
                "staffing_change": diff,
                "average_wait_minutes": round(new_wait, 1),
                "overloaded_slots": new_overload,
                "wait_reduction_minutes": round(max(0.0, baseline_wait - new_wait), 1),
                "overload_reduction_count": max(0, baseline_overload - new_overload),
                "disruption_score": 2,
                "feasibility": "Fully Feasible (Minimal Disruption)",
                "staff_budget": scenario.total_staff_available,
            })

    # -----------------------------------------------------------------------
    # Plan 3: Temporary Surge Float Staff (+1 buffer)
    # -----------------------------------------------------------------------
    if curr_target_staff < target_queue_cfg.max_staff:
        expanded_scenario = scenario.model_copy(
            update={"total_staff_available": scenario.total_staff_available + 1}
        )
        opt_exp = optimize(expanded_scenario, stressed_forecast)
        if opt_exp.feasible and opt_exp.optimized:
            exp_alloc = opt_exp.optimized.allocation.staff_by_queue
            sig = tuple(sorted(exp_alloc.items()))
            if sig not in seen_allocations:
                seen_allocations.add(sig)
                diff = {qid: exp_alloc.get(qid, 0) - current_allocation.staff_by_queue.get(qid, 0) for qid in exp_alloc}
                disruption = sum(abs(d) for d in diff.values())
                res = opt_exp.optimized.result
                new_wait = res.branch_wide.avg_wait_minutes
                new_overload = res.branch_wide.overloaded_slot_count

                plans.append({
                    "id": "plan-surge-buffer",
                    "title": "Deploy Surge Float Staff (+1 Staff Buffer)",
                    "strategy": "capacity_expansion",
                    "action": _describe_staffing_changes(diff, queue_names),
                    "resulting_allocation": exp_alloc,
                    "staffing_change": diff,
                    "average_wait_minutes": round(new_wait, 1),
                    "overloaded_slots": new_overload,
                    "wait_reduction_minutes": round(max(0.0, baseline_wait - new_wait), 1),
                    "overload_reduction_count": max(0, baseline_overload - new_overload),
                    "disruption_score": disruption,
                    "feasibility": "Conditional Feasible (+1 Temporary Float Staff)",
                    "staff_budget": expanded_scenario.total_staff_available,
                })

    # Deterministic ranking:
    # 1. Budget-neutral plans preferred over budget expansion
    # 2. Highest wait reduction
    # 3. Lowest disruption score
    def _rank_key(p: Dict[str, Any]) -> tuple:
        is_expanded = 1 if p["strategy"] == "capacity_expansion" else 0
        return (is_expanded, -p["wait_reduction_minutes"], p["disruption_score"])

    plans.sort(key=_rank_key)
    return plans

"""
backend/resilience/engine.py — Branch Stress Test and Resilience Engine.

Evaluates operational resilience under Demand Shock, Service-Time Shock,
Workforce Shock, and Combined Shock. Reuses the canonical deterministic
queue simulation and decision engine to calculate:
1. Progressive stress degradation
2. Simulated operational breakpoint (via dynamic bisection search)
3. Empirical primary bottleneck
4. Branch Resilience Score
5. Operational Recovery Plans
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

from backend.models import (
    AllocationPlan,
    ForecastResult,
    QueueConfig,
    ScenarioConfig,
    SimulationResult,
)
from backend.optimization.baseline import baseline_allocation
from backend.optimization.optimizer import optimize
from backend.resilience.recovery import find_recovery_plans
from backend.resilience.scorer import calculate_resilience_score
from backend.routes.custom_workload import (
    CustomTask,
    CustomWorkloadRequest,
    UnifiedTask,
    _apply_task_service_times,
    _build_custom_forecast,
    _classify_scenario,
)
from backend.simulation.engine import simulate
from data.scenarios import get_scenario

logger = logging.getLogger(__name__)

CRITICAL_WAIT_MINUTES_THRESHOLD = 15.0


class StressTestConfig(BaseModel):
    category: Literal["demand_shock", "service_time_shock", "workforce_shock", "combined_shock"] = "demand_shock"
    seed: int = 42


def _scale_forecast(forecast: ForecastResult, multiplier: float) -> ForecastResult:
    """Deterministically scale expected arrivals by a multiplier."""
    scaled_arrivals = {}
    for qid, arrivals in forecast.expected_arrivals.items():
        scaled_arrivals[qid] = [round(max(0.0, a * multiplier), 3) for a in arrivals]
    return ForecastResult(
        scenario_name=forecast.scenario_name,
        slots=list(forecast.slots),
        expected_arrivals=scaled_arrivals,
    )


def _scale_service_times(scenario: ScenarioConfig, multiplier: float) -> ScenarioConfig:
    """Scale average service times across all queues."""
    new_queues = []
    for q in scenario.queues:
        new_queues.append(
            q.model_copy(
                update={"avg_service_time_minutes": round(q.avg_service_time_minutes * multiplier, 2)}
            )
        )
    return scenario.model_copy(update={"queues": new_queues})


def _is_failure_condition(
    sim_result: SimulationResult,
    baseline_result: SimulationResult,
) -> Tuple[bool, str]:
    """
    Evaluate whether a simulation run breaches the branch operational tolerance.
    """
    bw = sim_result.branch_wide
    base_bw = baseline_result.branch_wide

    if bw.avg_wait_minutes >= CRITICAL_WAIT_MINUTES_THRESHOLD:
        return True, f"Average wait time ({bw.avg_wait_minutes:.1f} min) exceeds operational threshold ({CRITICAL_WAIT_MINUTES_THRESHOLD:.0f} min)."

    if base_bw.overloaded_slot_count == 0:
        if bw.overloaded_slot_count > 0:
            return True, f"Queue overload detected across {bw.overloaded_slot_count} time slot(s)."
    else:
        # If baseline was already overloaded (e.g. surge), failure triggers on 25%+ overload expansion
        if bw.overloaded_slot_count >= base_bw.overloaded_slot_count + 2:
            return True, f"Overloaded slots escalated from {base_bw.overloaded_slot_count} to {bw.overloaded_slot_count} slots."

    if bw.total_end_backlog > 0 and base_bw.total_end_backlog == 0:
        return True, f"Unserved backlog of {bw.total_end_backlog} customer(s) accumulated at closing."

    return False, "Operating within acceptable limits."


def _detect_bottleneck(
    stressed_result: SimulationResult,
    baseline_result: SimulationResult,
    scenario: ScenarioConfig,
) -> Dict[str, Any]:
    """Identify the queue responsible for primary operational degradation."""
    queue_names = {q.queue_id: q.name for q in scenario.queues}
    max_degradation = -1.0
    bottleneck_qid = scenario.queues[0].queue_id
    bottleneck_metric = "avg_wait_minutes"
    base_val = 0.0
    stress_val = 0.0
    reason = "Capacity exceeded."

    for qid, q_res in stressed_result.per_queue.items():
        base_q_res = baseline_result.per_queue.get(qid)
        b_wait = base_q_res.avg_wait_minutes if base_q_res else 0.0
        delta_wait = max(0.0, q_res.avg_wait_minutes - b_wait)
        overloads = len(q_res.overloaded_slots)
        backlog = q_res.end_backlog

        degradation = (delta_wait * 2.0) + (overloads * 4.0) + (backlog * 1.5)
        if degradation > max_degradation:
            max_degradation = degradation
            bottleneck_qid = qid
            base_val = b_wait
            stress_val = q_res.avg_wait_minutes
            name = queue_names.get(qid, qid.title())
            if overloads > 0:
                reason = f"{name} experienced {overloads} overloaded slots with wait rising from {b_wait:.1f}m to {q_res.avg_wait_minutes:.1f}m."
            else:
                reason = f"{name} wait time expanded from {b_wait:.1f}m to {q_res.avg_wait_minutes:.1f}m."

    return {
        "queue": bottleneck_qid,
        "queue_name": queue_names.get(bottleneck_qid, bottleneck_qid.title()),
        "reason": reason,
        "metric": bottleneck_metric,
        "baselineValue": round(base_val, 1),
        "stressedValue": round(stress_val, 1),
    }


def run_branch_stress_test(
    tasks: List[UnifiedTask],
    stress_config: Optional[StressTestConfig] = None,
) -> Dict[str, Any]:
    """
    Execute the full deterministic Branch Stress Test.
    """
    cfg = stress_config or StressTestConfig()
    category = cfg.category
    seed = cfg.seed

    workload_req = CustomWorkloadRequest(tasks=tasks, seed=seed)
    scenario_name, demand_multiplier = _classify_scenario(workload_req)
    base_scenario = get_scenario(scenario_name, seed=seed)
    scenario = _apply_task_service_times(base_scenario, workload_req)
    baseline_forecast = _build_custom_forecast(scenario, workload_req)

    # 1. Baseline Run
    baseline_plan = baseline_allocation(scenario)
    avg_service_times = {q.queue_id: q.avg_service_time_minutes for q in scenario.queues}
    baseline_sim = simulate(baseline_forecast, baseline_plan, avg_service_times, scenario.slot_minutes)

    # 2. Stress Scenario Definition
    if category == "demand_shock":
        steps = [
            {"id": "d-100", "label": "Baseline (1.00×)", "d_mult": 1.00, "s_mult": 1.0, "unavail": 0},
            {"id": "d-110", "label": "+10% Demand (1.10×)", "d_mult": 1.10, "s_mult": 1.0, "unavail": 0},
            {"id": "d-125", "label": "+25% Demand (1.25×)", "d_mult": 1.25, "s_mult": 1.0, "unavail": 0},
            {"id": "d-150", "label": "+50% Demand (1.50×)", "d_mult": 1.50, "s_mult": 1.0, "unavail": 0},
            {"id": "d-175", "label": "+75% Demand (1.75×)", "d_mult": 1.75, "s_mult": 1.0, "unavail": 0},
            {"id": "d-200", "label": "+100% Demand (2.00×)", "d_mult": 2.00, "s_mult": 1.0, "unavail": 0},
        ]
    elif category == "service_time_shock":
        steps = [
            {"id": "s-100", "label": "Baseline Duration (1.00×)", "d_mult": 1.0, "s_mult": 1.00, "unavail": 0},
            {"id": "s-110", "label": "+10% Duration (1.10×)", "d_mult": 1.0, "s_mult": 1.10, "unavail": 0},
            {"id": "s-125", "label": "+25% Duration (1.25×)", "d_mult": 1.0, "s_mult": 1.25, "unavail": 0},
            {"id": "s-150", "label": "+50% Duration (1.50×)", "d_mult": 1.0, "s_mult": 1.50, "unavail": 0},
        ]
    elif category == "workforce_shock":
        steps = [
            {"id": "w-0", "label": "Full Staff (0 absent)", "d_mult": 1.0, "s_mult": 1.0, "unavail": 0},
            {"id": "w-1", "label": "-1 Staff Unavailable", "d_mult": 1.0, "s_mult": 1.0, "unavail": 1},
            {"id": "w-2", "label": "-2 Staff Unavailable", "d_mult": 1.0, "s_mult": 1.0, "unavail": 2},
        ]
    else:  # combined_shock
        steps = [
            {"id": "c-0", "label": "Baseline Operating State", "d_mult": 1.0, "s_mult": 1.0, "unavail": 0},
            {"id": "c-1", "label": "Moderate (+20% D, +10% S)", "d_mult": 1.20, "s_mult": 1.10, "unavail": 0},
            {"id": "c-2", "label": "Severe (+35% D, +15% S, -1 Staff)", "d_mult": 1.35, "s_mult": 1.15, "unavail": 1},
            {"id": "c-3", "label": "Extreme (+50% D, +20% S, -1 Staff)", "d_mult": 1.50, "s_mult": 1.20, "unavail": 1},
        ]

    scenario_results = []
    first_failing_step = None
    last_safe_step = None

    for step in steps:
        step_scenario = _scale_service_times(scenario, step["s_mult"])
        step_budget = max(sum(q.min_staff for q in step_scenario.queues), step_scenario.total_staff_available - step["unavail"])
        step_scenario = step_scenario.model_copy(update={"total_staff_available": step_budget})
        step_forecast = _scale_forecast(baseline_forecast, step["d_mult"])

        # Determine step allocation (using baseline adjusted for staff reduction if necessary)
        if step["unavail"] > 0:
            step_alloc = baseline_allocation(step_scenario)
        else:
            step_alloc = baseline_plan

        step_times = {q.queue_id: q.avg_service_time_minutes for q in step_scenario.queues}
        step_sim = simulate(step_forecast, step_alloc, step_times, step_scenario.slot_minutes)

        is_fail, fail_reason = _is_failure_condition(step_sim, baseline_sim)
        step_bottleneck = _detect_bottleneck(step_sim, baseline_sim, step_scenario)

        entry = {
            "id": step["id"],
            "label": step["label"],
            "demandMultiplier": step["d_mult"],
            "serviceTimeMultiplier": step["s_mult"],
            "unavailableStaff": step["unavail"],
            "scenarioClassification": scenario_name,
            "allocation": step_alloc.staff_by_queue,
            "averageWait": round(step_sim.branch_wide.avg_wait_minutes, 1),
            "overloadedSlots": step_sim.branch_wide.overloaded_slot_count,
            "utilization": round(
                sum(qr.utilization for qr in step_sim.per_queue.values()) / max(1, len(step_sim.per_queue)), 2
            ),
            "failure": is_fail,
            "failureReason": fail_reason if is_fail else None,
            "bottleneck": step_bottleneck["queue_name"],
        }
        scenario_results.append(entry)

        if is_fail and first_failing_step is None:
            first_failing_step = (step, step_sim, step_bottleneck)
        if not is_fail:
            last_safe_step = (step, step_sim, step_bottleneck)

    # 3. Dynamic Breakpoint Bisection Search
    # Search the primary continuous dimension (demand or service time)
    if first_failing_step is None:
        # System survived all configured steps
        breakpoint_multiplier = round(steps[-1]["d_mult"] * 1.15, 2)
        breakpoint_reason = "Branch operates safely throughout all evaluated stress thresholds."
        effective_bottleneck = scenario_results[-1]["bottleneck"]
    elif last_safe_step is None:
        # Even baseline failed
        breakpoint_multiplier = 1.00
        breakpoint_reason = first_failing_step[1].branch_wide.avg_wait_minutes
        effective_bottleneck = first_failing_step[2]["queue_name"]
    else:
        # Bisection between last safe and first failing multiplier
        low = last_safe_step[0]["d_mult"] if category != "service_time_shock" else last_safe_step[0]["s_mult"]
        high = first_failing_step[0]["d_mult"] if category != "service_time_shock" else first_failing_step[0]["s_mult"]

        for _ in range(5):
            mid = (low + high) / 2.0
            if category == "service_time_shock":
                mid_scenario = _scale_service_times(scenario, mid)
                mid_forecast = baseline_forecast
            else:
                mid_scenario = scenario
                mid_forecast = _scale_forecast(baseline_forecast, mid)

            mid_times = {q.queue_id: q.avg_service_time_minutes for q in mid_scenario.queues}
            mid_sim = simulate(mid_forecast, baseline_plan, mid_times, mid_scenario.slot_minutes)
            is_mid_fail, _ = _is_failure_condition(mid_sim, baseline_sim)
            if is_mid_fail:
                high = mid
            else:
                low = mid

        breakpoint_multiplier = round(high, 2)
        effective_bottleneck = first_failing_step[2]["queue_name"]
        breakpoint_reason = (
            f"Overload threshold breached at ~{breakpoint_multiplier:.2f}× with {first_failing_step[2]['queue_name']} queue saturation."
        )

    # 4. Primary Bottleneck Identification
    # Use the first failing condition or the highest stress point
    target_stressed_sim = first_failing_step[1] if first_failing_step else scenario_results[-1]
    if first_failing_step:
        primary_bottleneck = first_failing_step[2]
        stressed_forecast_for_recovery = _scale_forecast(baseline_forecast, first_failing_step[0]["d_mult"])
        stressed_sim_for_recovery = first_failing_step[1]
    else:
        primary_bottleneck = _detect_bottleneck(baseline_sim, baseline_sim, scenario)
        stressed_forecast_for_recovery = _scale_forecast(baseline_forecast, steps[-1]["d_mult"])
        step_times = {q.queue_id: q.avg_service_time_minutes for q in scenario.queues}
        stressed_sim_for_recovery = simulate(stressed_forecast_for_recovery, baseline_plan, step_times, scenario.slot_minutes)

    # 5. Resilience Score Calculation
    # Find metrics at moderate stress (approx 1.25x or index 2)
    moderate_step = scenario_results[min(2, len(scenario_results) - 1)]
    overload_ratio = moderate_step["overloadedSlots"] / max(1, scenario.slot_count())
    wait_ratio = moderate_step["averageWait"] / max(0.5, baseline_sim.branch_wide.avg_wait_minutes)
    min_staff_req = sum(q.min_staff for q in scenario.queues)
    staff_buffer = (scenario.total_staff_available - min_staff_req) / max(1, scenario.total_staff_available)

    resilience = calculate_resilience_score(
        breakpoint_multiplier=breakpoint_multiplier,
        overload_rate_at_moderate_stress=overload_ratio,
        wait_escalation_ratio=wait_ratio,
        staffing_buffer_ratio=staff_buffer,
    )

    # 6. Recovery Plan Recommendations
    recovery_plans = find_recovery_plans(
        scenario=scenario,
        stressed_forecast=stressed_forecast_for_recovery,
        stressed_result=stressed_sim_for_recovery,
        current_allocation=baseline_plan,
        bottleneck_queue=primary_bottleneck["queue"],
    )

    return {
        "baseline": {
            "scenarioClassification": scenario_name,
            "demandMultiplier": round(demand_multiplier, 2),
            "allocation": baseline_plan.staff_by_queue,
            "averageWait": round(baseline_sim.branch_wide.avg_wait_minutes, 1),
            "overloadedSlots": baseline_sim.branch_wide.overloaded_slot_count,
            "totalStaff": scenario.total_staff_available,
        },
        "stressCategory": category,
        "stressScenarios": scenario_results,
        "breakpoint": {
            "multiplier": breakpoint_multiplier,
            "label": f"~{breakpoint_multiplier:.2f}× {'service duration' if category == 'service_time_shock' else 'demand'}",
            "failureReason": breakpoint_reason,
            "bottleneck": effective_bottleneck,
        },
        "bottleneck": primary_bottleneck,
        "resilienceScore": resilience["score"],
        "resilienceDetails": resilience,
        "recoveryPlans": recovery_plans,
        "assumptions": {
            "simulationSlotMinutes": scenario.slot_minutes,
            "criticalWaitThresholdMinutes": CRITICAL_WAIT_MINUTES_THRESHOLD,
            "seed": seed,
            "methodology": "Deterministic fixed-step simulation with binary search breakpoint estimation",
        },
    }

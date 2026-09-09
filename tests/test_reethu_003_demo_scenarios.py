"""
tests/test_reethu_003_demo_scenarios.py — demo scenario realism and validation.

Covers REETHU-003:
- canonical normal / peak / surge end-to-end behavior
- ADR-004 seed-42 benchmark regression values
- explanation traceability and deterministic content
- what-if operator trade-offs
- multi-seed robustness and runtime stability
"""
from __future__ import annotations

import re
import time

import pytest

from backend.forecasting.forecast import forecast
from backend.main import app
from backend.models import AllocationPlan
from backend.optimization.baseline import baseline_allocation
from backend.optimization.optimizer import W_OVERLOAD, W_UTIL, optimize
from backend.optimization.explain import explain_result
from backend.simulation.engine import simulate
from data.scenarios import get_scenario


SCENARIOS = ("normal", "peak", "surge")
SEEDS = (1, 7, 42, 99, 123, 2026)


def _avg_service_times(scenario):
    return {q.queue_id: q.avg_service_time_minutes for q in scenario.queues}


def _pipeline(name: str, seed: int = 42):
    scenario = get_scenario(name, seed=seed)
    fc = forecast(scenario)
    baseline = baseline_allocation(scenario)
    base_result = simulate(fc, baseline, _avg_service_times(scenario), scenario.slot_minutes)
    result = optimize(scenario, fc)
    return scenario, fc, baseline, base_result, result


def _assert_complete_result(result):
    assert result.feasible is True
    assert result.scenario_name in SCENARIOS
    assert result.baseline.result.branch_wide.total_served >= 0
    assert result.optimized.result.branch_wide.total_served >= 0
    assert result.baseline.allocation.total_staff() <= 10
    assert result.optimized.allocation.total_staff() <= 10
    assert set(result.baseline.result.per_queue) == {"teller", "loans", "customer_service"}
    assert set(result.optimized.result.per_queue) == {"teller", "loans", "customer_service"}


def test_demo_pipeline_normal_scenario_complete_flow():
    scenario, fc, baseline, base_result, result = _pipeline("normal")
    _assert_complete_result(result)
    assert base_result.branch_wide.avg_wait_minutes == pytest.approx(0.0)
    assert result.optimized.result.branch_wide.avg_wait_minutes == pytest.approx(0.0)
    assert result.optimized.allocation.staff_by_queue == {"teller": 4, "loans": 1, "customer_service": 2}
    assert result.improvement.avg_wait_reduction_minutes == pytest.approx(0.0)
    assert result.improvement.overloaded_slots_resolved == 0
    assert "NORMAL" in result.explanation


def test_demo_pipeline_peak_scenario_complete_flow():
    scenario, fc, baseline, base_result, result = _pipeline("peak")
    _assert_complete_result(result)
    assert base_result.branch_wide.avg_wait_minutes == pytest.approx(0.0)
    assert result.optimized.result.branch_wide.avg_wait_minutes == pytest.approx(0.0)
    assert result.optimized.allocation.staff_by_queue == {"teller": 4, "loans": 2, "customer_service": 3}
    assert result.improvement.avg_wait_reduction_minutes == pytest.approx(0.0)
    assert result.improvement.overloaded_slots_resolved == 0
    assert "PEAK" in result.explanation


def test_demo_pipeline_surge_scenario_complete_flow():
    scenario, fc, baseline, base_result, result = _pipeline("surge")
    _assert_complete_result(result)
    assert base_result.branch_wide.avg_wait_minutes == pytest.approx(93.66, abs=0.01)
    assert base_result.branch_wide.p95_wait_minutes == pytest.approx(153.87, abs=0.01)
    assert base_result.branch_wide.overloaded_slot_count == 25
    assert result.optimized.allocation.staff_by_queue == {"teller": 4, "loans": 3, "customer_service": 3}
    assert result.improvement.avg_wait_reduction_minutes == pytest.approx(0.0)
    assert result.improvement.overloaded_slots_resolved == 0
    assert "SURGE" in result.explanation
    assert "baseline is already optimal" in result.explanation


@pytest.mark.parametrize(
    "scenario_name,expected",
    [
        ("normal", {"avg": 0.0, "p95": 0.0, "overload": 0, "backlog": 0, "base_score": 0.048539, "opt_score": 0.016906}),
        ("peak", {"avg": 0.0, "p95": 0.0, "overload": 0, "backlog": 0, "base_score": 0.015317, "opt_score": 0.006139}),
        ("surge", {"avg": 93.66, "p95": 153.87, "overload": 25, "backlog": 153, "base_score": 0.505440, "opt_score": 0.505440}),
    ],
)
def test_adr004_benchmark_metrics_seed_42(scenario_name, expected):
    _, _, _, _, result = _pipeline(scenario_name)
    bw_base = result.baseline.result.branch_wide
    bw_opt = result.optimized.result.branch_wide
    assert bw_base.avg_wait_minutes == pytest.approx(expected["avg"], abs=0.01)
    assert bw_opt.avg_wait_minutes == pytest.approx(expected["avg"], abs=0.01)
    assert bw_base.p95_wait_minutes == pytest.approx(expected["p95"], abs=0.01)
    assert bw_opt.p95_wait_minutes == pytest.approx(expected["p95"], abs=0.01)
    assert bw_base.overloaded_slot_count == expected["overload"]
    assert bw_opt.overloaded_slot_count == expected["overload"]
    assert bw_base.total_end_backlog == expected["backlog"]
    assert bw_opt.total_end_backlog == expected["backlog"]
    assert result.baseline.score == pytest.approx(expected["base_score"], abs=1e-6)
    assert result.optimized.score == pytest.approx(expected["opt_score"], abs=1e-6)


def test_explanation_numbers_match_simulation_results():
    scenario, _, _, _, result = _pipeline("surge")
    explanation = result.explanation
    base = result.baseline.result.branch_wide
    opt = result.optimized.result.branch_wide
    improvement = result.improvement

    for value in (base.avg_wait_minutes, base.p95_wait_minutes, base.overloaded_slot_count,
                  opt.avg_wait_minutes, opt.p95_wait_minutes, improvement.avg_wait_reduction_minutes,
                  improvement.p95_wait_reduction_minutes, improvement.overloaded_slots_resolved):
        assert f"{value:.1f}" in explanation or f"{value:d}" in explanation
    assert scenario.scenario_name.upper() in explanation
    assert str(result.baseline.allocation.staff_by_queue["teller"]) in explanation


def test_explanation_staff_movement_text_matches_allocations():
    _, _, _, _, result = _pipeline("normal")
    explanation = result.explanation
    base = result.baseline.allocation.staff_by_queue
    opt = result.optimized.allocation.staff_by_queue
    for qid, base_staff in base.items():
        delta = opt[qid] - base_staff
        if delta < 0:
            assert f"{delta} from" in explanation
        elif delta > 0:
            assert f"+{delta} to" in explanation
    assert "Recommended allocation" in explanation


def test_explanation_weight_constants_match_optimizer_weights():
    """Regression guard: explanation must report the weights used by optimizer.py."""
    _, _, _, _, result = _pipeline("normal")
    explanation = result.explanation
    assert f"(x{W_OVERLOAD:.1f})" in explanation
    assert f"(x{W_UTIL:.1f})" in explanation


def test_surge_whatif_reallocation_demonstrates_tradeoff():
    scenario, fc, _, _, result = _pipeline("surge")
    base_alloc = result.baseline.allocation.staff_by_queue
    shifted = AllocationPlan(label="whatif", staff_by_queue={"teller": base_alloc["teller"] + 1, "loans": base_alloc["loans"] - 1, "customer_service": base_alloc["customer_service"]})
    shifted_result = simulate(fc, shifted, _avg_service_times(scenario), scenario.slot_minutes)
    base_loans = result.baseline.result.per_queue["loans"]
    shifted_loans = shifted_result.per_queue["loans"]
    assert shifted_loans.p95_wait_minutes > base_loans.p95_wait_minutes
    assert len(shifted_loans.overloaded_slots) >= len(base_loans.overloaded_slots)


def test_whatif_additional_staff_in_surge_relieves_bottleneck():
    scenario, fc, _, _, result = _pipeline("surge")
    base = result.baseline.result
    extra = AllocationPlan(label="whatif", staff_by_queue={"teller": 4, "loans": 4, "customer_service": 3})
    extra_result = simulate(fc, extra, _avg_service_times(scenario), scenario.slot_minutes)
    assert extra_result.per_queue["loans"].end_backlog < base.per_queue["loans"].end_backlog
    assert extra_result.branch_wide.total_end_backlog < base.branch_wide.total_end_backlog


def test_whatif_understaffing_normal_induces_overload():
    scenario, fc, _, _, result = _pipeline("normal")
    minimum = AllocationPlan(label="whatif", staff_by_queue={"teller": 1, "loans": 1, "customer_service": 1})
    minimum_result = simulate(fc, minimum, _avg_service_times(scenario), scenario.slot_minutes)
    assert minimum_result.branch_wide.overloaded_slot_count > 0
    assert minimum_result.branch_wide.total_end_backlog > 0
    assert minimum_result.branch_wide.avg_wait_minutes > 0


def test_whatif_execution_speed_under_target():
    scenario, fc, _, _, result = _pipeline("surge")
    allocation = AllocationPlan(label="whatif", staff_by_queue=result.baseline.allocation.staff_by_queue)
    start = time.perf_counter()
    simulate(fc, allocation, _avg_service_times(scenario), scenario.slot_minutes)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.1


def test_demo_scenarios_multi_seed_robustness():
    for seed in SEEDS:
        for name in SCENARIOS:
            scenario = get_scenario(name, seed=seed)
            fc = forecast(scenario)
            start = time.perf_counter()
            result = optimize(scenario, fc)
            elapsed = time.perf_counter() - start
            _assert_complete_result(result)
            assert elapsed < 1.0
            assert result.optimized.allocation.total_staff() <= scenario.total_staff_available
            for q in scenario.queues:
                assert q.min_staff <= result.optimized.allocation.staff_by_queue[q.queue_id] <= q.max_staff


def test_demo_demand_ordering_is_normal_peak_surge():
    totals = {}
    for name in SCENARIOS:
        fc = forecast(get_scenario(name, seed=42))
        totals[name] = sum(sum(values) for values in fc.expected_arrivals.values())
    assert totals["normal"] < totals["peak"] < totals["surge"]


def test_demo_surge_baseline_is_global_optimum_for_seed_42():
    scenario, fc, _, _, result = _pipeline("surge")
    assert result.optimized.allocation.staff_by_queue == result.baseline.allocation.staff_by_queue
    assert result.optimized.score == pytest.approx(result.baseline.score, abs=1e-6)
    assert result.improvement.avg_wait_reduction_minutes == pytest.approx(0.0)
    assert result.improvement.p95_wait_reduction_minutes == pytest.approx(0.0)
    assert result.improvement.overloaded_slots_resolved == 0


def test_explanation_contains_exhaustive_selection_statement():
    _, _, _, _, result = _pipeline("surge")
    assert "evaluated exhaustively" in result.explanation


def test_demo_pipeline_is_deterministic():
    first = _pipeline("surge", seed=42)[-1]
    second = _pipeline("surge", seed=42)[-1]
    assert first == second

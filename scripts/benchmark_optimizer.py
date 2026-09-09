"""
scripts/benchmark_optimizer.py — KIRAN-001 sizing benchmark.

Runs the REAL optimizer (not mocks) against normal/peak/surge scenarios
and records all required metrics. Output is deterministic (fixed seed).

Usage:
    python -m scripts.benchmark_optimizer

Do NOT fabricate or cherry-pick results.
"""

from __future__ import annotations

import itertools
import time
from typing import Dict

from backend.forecasting.forecast import forecast as run_forecast
from backend.optimization.baseline import baseline_allocation
from backend.optimization.optimizer import (
    enumerate_feasible_allocations,
    is_feasible,
    optimize,
)
from backend.simulation.engine import simulate
from data.scenarios import get_scenario

SEED = 42


def _avg_util(result) -> float:
    if not result.per_queue:
        return 0.0
    vals = [q.utilization for q in result.per_queue.values()]
    return sum(vals) / len(vals)


def benchmark_scenario(scenario_name: str) -> Dict:
    cfg = get_scenario(scenario_name, seed=SEED)
    fc = run_forecast(cfg)
    avg_service_times = {q.queue_id: q.avg_service_time_minutes for q in cfg.queues}

    # ── Feasible allocation count (enumeration only, no simulation) ──
    t_enum_start = time.perf_counter()
    feasible_allocs = enumerate_feasible_allocations(cfg)
    t_enum = time.perf_counter() - t_enum_start
    n_feasible = len(feasible_allocs)

    # ── Raw product space (before constraint filter) ──
    product_size = 1
    for q in cfg.queues:
        product_size *= (q.max_staff - q.min_staff + 1)

    # ── Single simulation runtime (baseline) ──
    base_plan = baseline_allocation(cfg)
    t_sim_start = time.perf_counter()
    base_result = simulate(fc, base_plan, avg_service_times, cfg.slot_minutes)
    t_sim = time.perf_counter() - t_sim_start

    # ── Full optimization runtime (real implementation) ──
    t_opt_start = time.perf_counter()
    opt_result = optimize(cfg, fc)
    t_opt = time.perf_counter() - t_opt_start

    # ── Constraint validity check on selected allocation ──
    selected = opt_result.optimized.allocation.staff_by_queue
    constraint_valid = is_feasible(selected, cfg)

    # ── Determinism check: run optimize again, compare allocation ──
    opt_result_2 = optimize(cfg, fc)
    deterministic = (
        opt_result_2.optimized.allocation.staff_by_queue == selected
        and opt_result_2.optimized.score == opt_result.optimized.score
    )

    return {
        "scenario":                    scenario_name,
        "queue_count":                 len(cfg.queues),
        "total_staff":                 cfg.total_staff_available,
        "product_space":               product_size,
        "feasible_allocation_count":   n_feasible,
        "enum_runtime_s":              round(t_enum, 6),
        "sim_runtime_s":               round(t_sim, 6),
        "opt_runtime_s":               round(t_opt, 6),
        "baseline_avg_wait_min":       round(base_result.branch_wide.avg_wait_minutes, 4),
        "optimized_avg_wait_min":      round(opt_result.optimized.result.branch_wide.avg_wait_minutes, 4),
        "baseline_p95_wait_min":       round(base_result.branch_wide.p95_wait_minutes, 4),
        "optimized_p95_wait_min":      round(opt_result.optimized.result.branch_wide.p95_wait_minutes, 4),
        "baseline_overloaded_slots":   base_result.branch_wide.overloaded_slot_count,
        "optimized_overloaded_slots":  opt_result.optimized.result.branch_wide.overloaded_slot_count,
        "baseline_end_backlog":        base_result.branch_wide.total_end_backlog,
        "optimized_end_backlog":       opt_result.optimized.result.branch_wide.total_end_backlog,
        "baseline_score":              round(opt_result.baseline.score, 6),
        "optimized_score":             round(opt_result.optimized.score, 6),
        "selected_allocation":         selected,
        "constraint_valid":            constraint_valid,
        "deterministic":               deterministic,
        "feasible":                    opt_result.feasible,
        "avg_wait_reduction_min":      round(opt_result.improvement.avg_wait_reduction_minutes, 4),
        "p95_wait_reduction_min":      round(opt_result.improvement.p95_wait_reduction_minutes, 4),
        "overloaded_slots_resolved":   opt_result.improvement.overloaded_slots_resolved,
    }


def print_report(results: list[Dict], outfile: str = "benchmark_results.txt") -> None:
    SEP = "-" * 72
    lines_out = []
    def emit(s=""):
        lines_out.append(s)
        print(s)

    emit("\n" + SEP)
    emit("KIRAN-001 - Optimization Sizing Benchmark")
    emit(f"Seed: {SEED}   Target: sim < 1.0s, opt < 3.0s")
    emit(SEP)

    for r in results:
        sc = r["scenario"].upper()
        sim_ok  = "PASS" if r["sim_runtime_s"] < 1.0 else "FAIL: OVER TARGET"
        opt_ok  = "PASS" if r["opt_runtime_s"] < 3.0 else "FAIL: OVER TARGET"
        det_ok  = "PASS" if r["deterministic"] else "FAIL: NON-DETERMINISTIC"
        con_ok  = "PASS" if r["constraint_valid"] else "FAIL: CONSTRAINT VIOLATED"
        imp_ok  = "PASS" if r["optimized_score"] <= r["baseline_score"] + 1e-9 else "FAIL: WORSE THAN BASELINE"

        emit(f"\n{'='*30} {sc} {'='*30}")
        emit(f"  Queues: {r['queue_count']}   Total staff: {r['total_staff']}")
        emit(f"  Product space:            {r['product_space']:>6}")
        emit(f"  Feasible allocations:     {r['feasible_allocation_count']:>6}")
        emit(f"  Enum runtime:             {r['enum_runtime_s']:.6f}s")
        emit(f"  Single sim runtime:       {r['sim_runtime_s']:.6f}s  {sim_ok}")
        emit(f"  Full opt runtime:         {r['opt_runtime_s']:.6f}s  {opt_ok}")
        emit(f"  Baseline avg wait:        {r['baseline_avg_wait_min']:.4f} min")
        emit(f"  Optimized avg wait:       {r['optimized_avg_wait_min']:.4f} min  (reduction: {r['avg_wait_reduction_min']:.4f})")
        emit(f"  Baseline p95 wait:        {r['baseline_p95_wait_min']:.4f} min")
        emit(f"  Optimized p95 wait:       {r['optimized_p95_wait_min']:.4f} min  (reduction: {r['p95_wait_reduction_min']:.4f})")
        emit(f"  Baseline overloaded slots:{r['baseline_overloaded_slots']:>4}")
        emit(f"  Optimized overloaded slots:{r['optimized_overloaded_slots']:>3}  (resolved: {r['overloaded_slots_resolved']})")
        emit(f"  Baseline end backlog:     {r['baseline_end_backlog']:>4}")
        emit(f"  Optimized end backlog:    {r['optimized_end_backlog']:>4}")
        emit(f"  Baseline score:           {r['baseline_score']:.6f}")
        emit(f"  Optimized score:          {r['optimized_score']:.6f}  {imp_ok}")
        emit(f"  Selected allocation:      {r['selected_allocation']}")
        emit(f"  Constraint valid:         {con_ok}")
        emit(f"  Deterministic:            {det_ok}")

    emit("\n" + SEP)
    fails = [r for r in results if not (
        r["sim_runtime_s"] < 1.0
        and r["opt_runtime_s"] < 3.0
        and r["constraint_valid"]
        and r["deterministic"]
        and r["optimized_score"] <= r["baseline_score"] + 1e-9
        and r["feasible"]
    )]
    if fails:
        emit(f"FAILURES: {[f['scenario'] for f in fails]}")
    else:
        emit("ALL CHECKS PASSED. Exhaustive enumeration meets P0 targets.")
    emit(SEP + "\n")

    with open(outfile, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines_out))
    print(f"[Results also written to {outfile}]")


if __name__ == "__main__":
    results = []
    for scenario_name in ("normal", "peak", "surge"):
        print(f"Benchmarking {scenario_name}...", end=" ", flush=True)
        r = benchmark_scenario(scenario_name)
        results.append(r)
        print("done")
    print_report(results)

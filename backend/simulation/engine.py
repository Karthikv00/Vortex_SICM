"""
backend/simulation/engine.py — Fixed-width time-step queue simulation engine.

Core algorithm per slot per queue:
  1. Add expected arrivals to backlog.
  2. Compute available server-minutes = staff_count × slot_minutes.
  3. Serve backlog up to available server-minutes (FIFO, avg service time per customer).
  4. Carry unserved backlog forward — it accrues wait time.
  5. Record per-slot metrics.

At horizon end, compute:
  - per-queue: avg wait, p95 wait, mean utilization, overloaded slots, end backlog
  - branch-wide: weighted averages across queues

This module has NO dependency on FastAPI, HTTP, or UI. It is callable directly
from tests and the optimizer.

Implements: KARTHI-003
ADR-003:    Fixed-width time-step simulation
Spec:       docs/architecture/simulation-design.md
"""

from __future__ import annotations

import statistics
from typing import Dict, List

from backend.models import (
    AllocationPlan,
    BranchWideMetrics,
    ForecastResult,
    QueueSimResult,
    SimulationResult,
)

# ---------------------------------------------------------------------------
# Configuration constants — centralised here, not scattered through code.
# ---------------------------------------------------------------------------

# A slot is "overloaded" when backlog exceeds this multiple of staff count.
# Spec: docs/architecture/simulation-design.md line 13.
OVERLOAD_BACKLOG_MULTIPLE = 2


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _percentile(data: List[float], pct: float) -> float:
    """
    Compute the p-th percentile of a sorted data list using linear interpolation.

    Returns 0.0 for empty lists (zero-arrivals / zero-staff edge cases).
    """
    if not data:
        return 0.0
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]
    # Linear interpolation (same as numpy default)
    index = (pct / 100) * (n - 1)
    lo = int(index)
    hi = lo + 1
    if hi >= n:
        return sorted_data[-1]
    frac = index - lo
    return sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo])


# ---------------------------------------------------------------------------
# Per-queue simulation
# ---------------------------------------------------------------------------

def _simulate_queue(
    queue_id: str,
    arrivals: List[float],
    staff_count: int,
    avg_service_time_minutes: float,
    slot_minutes: int,
    slot_labels: List[str],
) -> QueueSimResult:
    """
    Run the time-step simulation for a single queue.

    Parameters
    ----------
    queue_id:                 identifier (used for error messages only)
    arrivals:                 expected arrivals per slot (float, may be fractional)
    staff_count:              staff assigned to this queue (integer ≥ 0)
    avg_service_time_minutes: average service time per customer (minutes)
    slot_minutes:             width of each time slot (minutes)
    slot_labels:              HH:MM label for each slot (for overload reporting)

    Returns
    -------
    QueueSimResult with per-queue aggregated metrics.
    """
    n_slots = len(arrivals)
    backlog: float = 0.0          # Customers waiting + partially-in-service
    total_served: int = 0

    # Per-slot records for post-processing
    slot_waits: List[float] = []  # Average wait contribution per slot
    slot_utils: List[float] = []  # Utilization per slot
    overloaded_slots: List[str] = []

    # Accumulate wait-time samples for p95 computation.
    # We approximate per-customer wait as: backlog_at_start_of_slot / service_rate
    wait_samples: List[float] = []

    for i, arrivals_this_slot in enumerate(arrivals):
        if arrivals_this_slot < 0:
            raise ValueError(
                f"Arrivals for queue '{queue_id}' at slot "
                f"'{slot_labels[i]}' cannot be negative"
            )

        # ----------------------------------------------------------------
        # 1. Add arrivals to backlog
        # ----------------------------------------------------------------
        backlog += arrivals_this_slot

        # ----------------------------------------------------------------
        # 2. Available service capacity this slot
        # ----------------------------------------------------------------
        if avg_service_time_minutes <= 0:
            raise ValueError(
                f"Queue '{queue_id}': avg_service_time_minutes must be > 0, "
                f"got {avg_service_time_minutes}"
            )

        server_minutes_available = staff_count * slot_minutes
        customers_serveable = server_minutes_available / avg_service_time_minutes

        # ----------------------------------------------------------------
        # 3. Serve backlog (up to capacity)
        # ----------------------------------------------------------------
        if backlog > 0 and customers_serveable > 0:
            served_this_slot = min(backlog, customers_serveable)
            server_minutes_used = served_this_slot * avg_service_time_minutes
        else:
            served_this_slot = 0.0
            server_minutes_used = 0.0

        # ----------------------------------------------------------------
        # 4. Wait-time approximation
        #    Customers who arrived this slot waited proportionally to the
        #    backlog that existed before they were served this slot.
        #    If backlog > capacity, arrivals wait at least one full slot.
        # ----------------------------------------------------------------
        if arrivals_this_slot > 0:
            if customers_serveable == 0:
                # Zero staff: nobody is served; every arrival accumulates wait
                wait_for_arrivals = slot_minutes  # At minimum they wait this slot
            else:
                # Wait proportional to queue position
                # Customers at back of queue wait: (backlog - served) / service_rate * slot_minutes
                residual = max(0.0, backlog - customers_serveable)
                wait_for_arrivals = (residual / max(customers_serveable, 1e-9)) * slot_minutes

            # Record a wait sample for each integer arrival (approximation)
            n_arrivals = max(1, round(arrivals_this_slot))
            wait_samples.extend([wait_for_arrivals] * n_arrivals)
            slot_waits.append(wait_for_arrivals)
        else:
            slot_waits.append(0.0)

        # ----------------------------------------------------------------
        # 5. Update backlog, record served
        # ----------------------------------------------------------------
        backlog = max(0.0, backlog - served_this_slot)
        total_served += round(served_this_slot)

        # ----------------------------------------------------------------
        # 6. Utilization = server-minutes used / available (0 if no staff)
        # ----------------------------------------------------------------
        if server_minutes_available > 0:
            utilization = min(1.0, server_minutes_used / server_minutes_available)
        else:
            utilization = 0.0
        slot_utils.append(utilization)

        # ----------------------------------------------------------------
        # 7. Overload detection
        #    Overloaded if backlog > OVERLOAD_BACKLOG_MULTIPLE × staff_count
        #    For zero staff: any backlog > 0 is overloaded.
        # ----------------------------------------------------------------
        overload_threshold = (
            0
            if staff_count == 0
            else OVERLOAD_BACKLOG_MULTIPLE * staff_count
        )
        if backlog > overload_threshold:
            overloaded_slots.append(slot_labels[i])
    # ----------------------------------------------------------------
    # Aggregate per-queue metrics
    # ----------------------------------------------------------------
    avg_wait = statistics.mean(wait_samples) if wait_samples else 0.0
    p95_wait = _percentile(wait_samples, 95) if wait_samples else 0.0
    mean_util = statistics.mean(slot_utils) if slot_utils else 0.0

    return QueueSimResult(
        avg_wait_minutes=round(avg_wait, 4),
        p95_wait_minutes=round(p95_wait, 4),
        utilization=round(mean_util, 4),
        overloaded_slots=overloaded_slots,
        total_served=total_served,
        end_backlog=round(backlog),
    )


# ---------------------------------------------------------------------------
# Main public entry point
# ---------------------------------------------------------------------------

def simulate(
    forecast: ForecastResult,
    allocation: AllocationPlan,
    avg_service_times: Dict[str, float],
    slot_minutes: int = 15,
) -> SimulationResult:
    """
    Run the full branch simulation for one allocation plan.

    Parameters
    ----------
    forecast:            Demand forecast (arrivals per queue per slot).
    allocation:          Staff allocation to evaluate.
    avg_service_times:   queue_id → avg_service_time_minutes mapping.
    slot_minutes:        Slot width in minutes (default 15).

    Returns
    -------
    SimulationResult containing per-queue and branch-wide metrics.

    Raises
    ------
    ValueError  — missing queue in allocation or avg_service_times, or invalid inputs.
    """
    if slot_minutes <= 0:
        raise ValueError(f"slot_minutes must be > 0, got {slot_minutes}")

    slot_labels = forecast.slots

    per_queue_results: Dict[str, QueueSimResult] = {}

    for queue_id, arrivals in forecast.expected_arrivals.items():
        if queue_id not in allocation.staff_by_queue:
            raise ValueError(
                f"Queue '{queue_id}' is in the forecast but not in the allocation. "
                f"Allocation keys: {list(allocation.staff_by_queue)}"
            )
        if queue_id not in avg_service_times:
            raise ValueError(
                f"Queue '{queue_id}' is in the forecast but not in avg_service_times."
            )

        staff = allocation.staff_by_queue[queue_id]
        if staff < 0:
            raise ValueError(f"Queue '{queue_id}': staff count cannot be negative, got {staff}")

        result = _simulate_queue(
            queue_id=queue_id,
            arrivals=arrivals,
            staff_count=staff,
            avg_service_time_minutes=avg_service_times[queue_id],
            slot_minutes=slot_minutes,
            slot_labels=slot_labels,
        )
        per_queue_results[queue_id] = result

    # ----------------------------------------------------------------
    # Branch-wide aggregation
    # ----------------------------------------------------------------
    all_wait_samples: List[float] = []
    total_served_all = 0
    total_backlog_all = 0
    overloaded_slot_set: set = set()

    # Collect per-queue wait samples (approximated from per-queue avg/p95)
    for qid, qr in per_queue_results.items():
        total_served_all += qr.total_served
        total_backlog_all += qr.end_backlog
        for s in qr.overloaded_slots:
            overloaded_slot_set.add(s)
        # Re-approximate per-queue contribution to branch-wide wait
        # weighted by total_served in that queue
        if qr.total_served > 0:
            all_wait_samples.extend([qr.avg_wait_minutes] * qr.total_served)

    branch_avg_wait = statistics.mean(all_wait_samples) if all_wait_samples else 0.0
    branch_p95_wait = _percentile(all_wait_samples, 95) if all_wait_samples else 0.0

    branch_wide = BranchWideMetrics(
        avg_wait_minutes=round(branch_avg_wait, 4),
        p95_wait_minutes=round(branch_p95_wait, 4),
        overloaded_slot_count=len(overloaded_slot_set),
        total_served=total_served_all,
        total_end_backlog=total_backlog_all,
    )

    return SimulationResult(
        allocation_label=allocation.label,
        per_queue=per_queue_results,
        branch_wide=branch_wide,
    )

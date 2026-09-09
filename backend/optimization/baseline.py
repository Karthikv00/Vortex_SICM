"""
backend/optimization/baseline.py — Deterministic baseline allocation strategy.

The baseline represents a reasonable "basic" operational approach:
  Proportional allocation — distribute staff in proportion to each queue's
  minimum-staff share of the total minimum requirement, then distribute
  any remaining staff to queues with the highest base rate (teller-priority).

The baseline must be:
- Deterministic (same scenario → same allocation every run)
- Feasible (respects all hard constraints)
- Reproducible (no randomness)
- "Basic but sensible" — not a deliberately bad strawman

The same baseline is used for comparison with the optimized allocation.
Never change the baseline logic mid-run; it must be identical for both the
baseline evaluation and as the reference in reallocation cost scoring.

Implements: KIRAN-004
Spec:       docs/architecture/optimization-design.md
            docs/requirements/functional-requirements.md FR-OPT-4
"""

from __future__ import annotations

from backend.models import AllocationPlan, ScenarioConfig


class InfeasibleBaselineError(Exception):
    """Raised when total_staff < sum of queue minimums."""


def baseline_allocation(scenario: ScenarioConfig) -> AllocationPlan:
    """
    Compute the deterministic proportional baseline allocation.

    Algorithm:
    1. Assign each queue its minimum required staff (min_staff).
    2. Check feasibility: if sum(min_staff) > total_staff_available, raise
       InfeasibleBaselineError — the scenario itself is infeasible.
    3. Distribute remaining staff proportionally to min_staff weights.
    4. Any integer-rounding remainder is given to the queue with the
       highest min_staff (tie: first in list order) — deterministic.

    Returns an AllocationPlan with label='baseline'.
    """
    queues = scenario.queues
    total = scenario.total_staff_available

    # Step 1: assign minimums
    allocation: dict[str, int] = {q.queue_id: q.min_staff for q in queues}
    assigned = sum(allocation.values())

    # Step 2: feasibility check
    if assigned > total:
        raise InfeasibleBaselineError(
            f"Sum of queue minimums ({assigned}) exceeds total_staff_available ({total}). "
            f"No feasible allocation exists."
        )

    # Step 3: distribute remainder proportionally to min_staff weights
    remainder = total - assigned
    if remainder > 0:
        # Weight each queue by its min_staff (floor of 1 for zero-min queues)
        weights = [max(q.min_staff, 1) for q in queues]
        total_weight = sum(weights)

        # Compute float shares
        shares = [remainder * w / total_weight for w in weights]

        # Floor to integers
        int_shares = [int(s) for s in shares]
        distributed = sum(int_shares)

        # Step 4: give integer rounding remainder to highest-min queue (deterministic)
        leftover = remainder - distributed
        if leftover > 0:
            # Sort by (min_staff DESC, index ASC) for deterministic tie-break
            order = sorted(
                range(len(queues)),
                key=lambda i: (-queues[i].min_staff, i)
            )
            for idx in order[:leftover]:
                int_shares[idx] += 1

        for i, q in enumerate(queues):
            # Clamp to max_staff
            extra = min(int_shares[i], q.max_staff - allocation[q.queue_id])
            allocation[q.queue_id] += extra

    return AllocationPlan(label="baseline", staff_by_queue=allocation)

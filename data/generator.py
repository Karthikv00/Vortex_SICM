"""
data/generator.py — Deterministic synthetic customer arrival data generator.

Generates reproducible arrival counts per queue per time slot using
seeded random variation around time-of-day base rates that vary by scenario.

Every random call is traceable to ScenarioConfig.seed, satisfying
FR-DATA-3 (reproducibility) and TC-01 (same seed + scenario → identical output).

Implements: KARTHI-001
Spec:        docs/requirements/functional-requirements.md FR-DATA-1 through FR-DATA-4
             docs/architecture/simulation-design.md
"""

from __future__ import annotations

import random
from typing import Dict, List

from backend.models import ForecastResult, ScenarioConfig

# ---------------------------------------------------------------------------
# Base arrival rates per queue (customers per 15-minute slot) — NORMAL scenario.
# These represent a realistic small bank branch.
#
# Time-of-day shape: low at open, ramp up, lunch dip, afternoon, tail off.
# Shape is expressed as a multiplier applied to each slot index (0-based).
# ---------------------------------------------------------------------------

# Base arrival rates (customers/slot at 100% load)
_BASE_RATES: Dict[str, float] = {
    "teller": 5.0,       # High-volume cash/deposit queue
    "loans": 1.2,        # Low-volume, appointment-driven
    "customer_service": 2.5,  # Medium-volume
}

# Scenario demand multipliers (applied uniformly across the day)
_SCENARIO_MULTIPLIERS: Dict[str, float] = {
    "normal": 1.0,
    "peak": 1.7,
    "surge": 2.8,
}

# Fallback for queues not listed in _BASE_RATES (safe default)
_DEFAULT_BASE_RATE = 2.0


def _time_of_day_shape(slot_index: int, total_slots: int) -> float:
    """
    Return a multiplier [0.4 – 1.0] that shapes demand across the day.

    The shape follows a typical bank branch pattern:
    - Moderate at opening (slots 0–3, i.e. 09:00–09:45)
    - Morning peak (slots 4–12, i.e. 10:00–12:00)
    - Lunch trough (slots 12–16, i.e. 12:00–13:00)
    - Afternoon recovery (slots 16–20, i.e. 13:00–14:00)
    - Gradual tail-off toward closing

    Total_slots for a 09:00–17:00 / 15-min horizon = 32.
    """
    # Normalised position [0, 1]
    t = slot_index / max(total_slots - 1, 1)

    # Piecewise shape
    if t < 0.1:        # Opening ramp
        return 0.5 + t * 3.0
    elif t < 0.40:     # Morning peak
        return 1.0
    elif t < 0.55:     # Lunch dip
        return 0.6 + (t - 0.40) * 0.8
    elif t < 0.75:     # Afternoon
        return 0.85
    else:              # End-of-day tail
        return max(0.4, 0.85 - (t - 0.75) * 2.0)


def _surge_shape_boost(slot_index: int, total_slots: int) -> float:
    """
    Additional multiplicative boost for the surge scenario,
    concentrated in the 10:00–14:00 window (slots 4–20 of a 09:00 horizon).
    """
    t = slot_index / max(total_slots - 1, 1)
    if 0.12 <= t <= 0.62:  # Surge window
        # Gaussian-like peak centred at t=0.37 (≈ 11:45)
        centre = 0.37
        width = 0.20
        boost = 1.5 * (1 - ((t - centre) / width) ** 2)
        return max(0.0, boost)
    return 0.0


def generate_arrivals(scenario: ScenarioConfig) -> Dict[str, List[int]]:
    """
    Generate synthetic customer arrival counts per queue per time slot.

    Returns a dict mapping queue_id → list[int] of integer arrival counts,
    one per slot. All values are >= 0.

    Deterministic for a given (scenario_name, seed).
    """
    rng = random.Random(scenario.seed)
    total_slots = scenario.slot_count()
    multiplier = _SCENARIO_MULTIPLIERS.get(scenario.scenario_name, 1.0)

    arrivals: Dict[str, List[int]] = {}

    for queue in scenario.queues:
        base_rate = _BASE_RATES.get(queue.queue_id, _DEFAULT_BASE_RATE)
        slot_arrivals: List[int] = []

        for i in range(total_slots):
            tod_factor = _time_of_day_shape(i, total_slots)

            # Surge gets an extra concentrated boost
            if scenario.scenario_name == "surge":
                tod_factor += _surge_shape_boost(i, total_slots)

            expected = base_rate * multiplier * tod_factor

            # Add Poisson-like variation: ±20% of expected, floor at 0
            noise = rng.uniform(-0.20, 0.20) * expected
            count = max(0, round(expected + noise))
            slot_arrivals.append(count)

        arrivals[queue.queue_id] = slot_arrivals

    return arrivals


def generate_slot_labels(scenario: ScenarioConfig) -> List[str]:
    """
    Return time-slot labels as 'HH:MM' strings covering the full horizon.

    Example for 09:00–17:00 with 15-min slots:
    ['09:00', '09:15', '09:30', ..., '16:45']
    """
    start_h, start_m = map(int, scenario.horizon_start.split(":"))
    start_total = start_h * 60 + start_m

    labels = []
    for i in range(scenario.slot_count()):
        t = start_total + i * scenario.slot_minutes
        h, m = divmod(t, 60)
        labels.append(f"{h:02d}:{m:02d}")
    return labels


def generate(scenario: ScenarioConfig) -> ForecastResult:
    """
    Generate a ForecastResult (raw arrivals, no smoothing) for a scenario.

    This is the data-generation entry point. The forecasting module applies
    time-of-day × scenario smoothing on top; here we return the seed-
    reproducible raw counts that serve as historical/observed data.

    Satisfies FR-DATA-1, FR-DATA-2, FR-DATA-3, FR-DATA-4.
    """
    slots = generate_slot_labels(scenario)
    arrivals = generate_arrivals(scenario)

    # ForecastResult validation will catch any length mismatches
    return ForecastResult(
        scenario_name=scenario.scenario_name,
        slots=slots,
        expected_arrivals={qid: list(map(float, counts)) for qid, counts in arrivals.items()},
    )

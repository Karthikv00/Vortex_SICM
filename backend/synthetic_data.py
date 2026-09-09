"""Deterministic synthetic customer-arrival data generator.

The generator is intentionally independent of FastAPI and the rest of the
application so it can be tested and reused by forecasting/simulation code.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

ScenarioName = Literal["normal", "peak", "surge"]

# Relative arrival-rate multipliers by scenario. Keeping these here makes the
# scenario behaviour explicit and easy to tune without changing the algorithm.
SCENARIO_MULTIPLIERS: dict[ScenarioName, float] = {
    "normal": 1.0,
    "peak": 1.35,
    "surge": 1.80,
}

# A simple time-of-day profile for the default 09:00-17:00 operating window.
# Values are deliberately distinct from scenario multipliers: time-of-day is
# demand shape, while scenario is demand intensity.
TIME_OF_DAY_FACTORS = (0.75, 0.85, 1.00, 1.15, 1.30, 1.20, 1.05, 0.95, 1.10, 1.25, 1.35, 1.15, 1.00, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 0.95, 0.90)


@dataclass(frozen=True)
class QueueConfig:
    """Minimum queue configuration needed to generate arrivals."""

    queue_id: str
    base_arrivals_per_slot: float


@dataclass(frozen=True)
class ScenarioConfig:
    """Synthetic-data generation configuration matching the shared contract."""

    scenario_name: ScenarioName
    seed: int
    horizon_start: str = "09:00"
    horizon_end: str = "17:00"
    slot_minutes: int = 15
    queues: tuple[QueueConfig, ...] = ()


def _time_to_minutes(value: str) -> int:
    try:
        hours, minutes = (int(part) for part in value.split(":", 1))
    except (ValueError, TypeError) as exc:
        raise ValueError("time must use HH:MM format") from exc
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError("time must use a valid 24-hour clock value")
    return hours * 60 + minutes


def _slots(config: ScenarioConfig) -> list[str]:
    start = _time_to_minutes(config.horizon_start)
    end = _time_to_minutes(config.horizon_end)
    if end <= start:
        raise ValueError("horizon_end must be after horizon_start")
    if config.slot_minutes <= 0:
        raise ValueError("slot_minutes must be positive")
    if (end - start) % config.slot_minutes:
        raise ValueError("horizon length must be divisible by slot_minutes")

    return [
        f"{minute // 60:02d}:{minute % 60:02d}"
        for minute in range(start, end, config.slot_minutes)
    ]


def _poisson(rng: random.Random, mean: float) -> int:
    """Sample a Poisson count using only the Python standard library."""
    if mean <= 0:
        return 0
    # Knuth's method is simple and sufficient for the small per-slot rates
    # used by the hackathon's synthetic queues.
    threshold = pow(2.718281828459045, -mean)
    product = 1.0
    count = 0
    while product > threshold:
        count += 1
        product *= rng.random()
    return count - 1


def generate_arrivals(config: ScenarioConfig) -> dict[str, list[int]]:
    """Generate deterministic arrivals keyed by queue id.

    The same config, including seed, always returns the same result. Queue
    generation uses one seeded RNG in a stable queue/slot order.
    """
    if config.scenario_name not in SCENARIO_MULTIPLIERS:
        raise ValueError("scenario_name must be one of: normal, peak, surge")
    if not config.queues:
        raise ValueError("at least one queue is required")
    queue_ids = [queue.queue_id for queue in config.queues]
    if any(not queue_id for queue_id in queue_ids):
        raise ValueError("queue_id must not be empty")
    if len(set(queue_ids)) != len(queue_ids):
        raise ValueError("queue_id values must be unique")
    if any(queue.base_arrivals_per_slot < 0 for queue in config.queues):
        raise ValueError("base_arrivals_per_slot must be non-negative")

    slots = _slots(config)
    rng = random.Random(config.seed)
    scenario_multiplier = SCENARIO_MULTIPLIERS[config.scenario_name]
    start = _time_to_minutes(config.horizon_start)
    arrivals: dict[str, list[int]] = {queue.queue_id: [] for queue in config.queues}

    for queue in config.queues:
        for slot in slots:
            minute_of_day = _time_to_minutes(slot)
            slot_index = (minute_of_day - start) // config.slot_minutes
            factor = TIME_OF_DAY_FACTORS[slot_index % len(TIME_OF_DAY_FACTORS)]
            mean = queue.base_arrivals_per_slot * factor * scenario_multiplier
            arrivals[queue.queue_id].append(_poisson(rng, mean))

    return arrivals

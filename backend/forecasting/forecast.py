"""
backend/forecasting/forecast.py — Demand forecast engine.

Converts raw synthetic arrival data from the generator into a smoothed
ForecastResult suitable for the simulation engine.

Forecasting approach (deterministic, no ML):
  - Use the raw generated arrivals as the "historical" base.
  - Apply a time-of-day factor × scenario multiplier on top.
  - Smooth with a 3-slot rolling average to remove spike artifacts.

This keeps forecasting explainable and entirely deterministic.

Implements: KARTHI-004
Spec:       docs/requirements/functional-requirements.md FR-FCST-1/2/3
            docs/architecture/TRD.md (Deterministic time-of-day factor × scenario multiplier)
"""

from __future__ import annotations

from typing import Dict, List

from backend.models import ForecastResult, ScenarioConfig
from data.generator import generate


# ---------------------------------------------------------------------------
# Scenario-level forecast multipliers (applied on top of generator output)
# ---------------------------------------------------------------------------
_FORECAST_MULTIPLIERS: Dict[str, float] = {
    "normal": 1.0,
    "peak": 1.0,   # Generator already applies peak multiplier; forecast pass-through
    "surge": 1.0,  # Same — pass-through; adjust here if smoothing changes shape
}


def _rolling_average(data: List[float], window: int = 3) -> List[float]:
    """
    Apply a simple rolling average with a given window size.
    Edges are padded with the first/last value so output length equals input.
    Returns 0.0 for any negative values (safety guard).
    """
    n = len(data)
    if n == 0:
        return []
    smoothed = []
    half = window // 2
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        avg = sum(data[lo:hi]) / (hi - lo)
        smoothed.append(max(0.0, avg))
    return smoothed


def forecast(scenario: ScenarioConfig) -> ForecastResult:
    """
    Generate a demand forecast for a scenario.

    Steps:
    1. Generate raw arrival data from the deterministic generator.
    2. Apply rolling-average smoothing (window=3 slots ≈ 45 min) to reduce
       slot-to-slot noise while preserving the surge shape.
    3. Return a ForecastResult consumable directly by the simulation engine.

    Scenario scaling (normal/peak/surge) and time-of-day shaping are applied
    by the data generator.  _FORECAST_MULTIPLIERS are intentionally 1.0
    (pass-through) so the forecasting layer does not double-count those
    effects.  Its primary value-add is deterministic smoothing.

    Fallback (FR-FCST-3): if generated data has all-zero arrivals for a queue
    (e.g. very short horizon or zero base rate), the forecast returns zeros
    without crashing — the simulation handles zero-arrival queues gracefully.
    """
    if not scenario.queues:
        raise ValueError("Scenario must define at least one queue for forecasting")

    raw: ForecastResult = generate(scenario)

    smoothed_arrivals: Dict[str, List[float]] = {}
    multiplier = _FORECAST_MULTIPLIERS.get(scenario.scenario_name, 1.0)

    for queue_id, raw_counts in raw.expected_arrivals.items():
        # Apply multiplier (currently 1.0 for all; hook for future tuning)
        scaled = [v * multiplier for v in raw_counts]
        # Smooth — reduces spike noise while keeping surge visible
        smoothed = _rolling_average(scaled, window=3)
        smoothed_arrivals[queue_id] = smoothed

    return ForecastResult(
        scenario_name=scenario.scenario_name,
        slots=raw.slots,
        expected_arrivals=smoothed_arrivals,
    )

"""
backend/resilience/scorer.py — Deterministic Branch Resilience Scoring.

Computes an explainable 0–100 Branch Resilience Score based on:
1. Demand Headroom: distance from normal load to operational breakpoint.
2. Overload Sensitivity: fraction of slots overloaded under moderate stress (1.25x).
3. Queue Stability: wait time growth curve and backlog acceleration.
4. Staffing Flexibility: operational buffer above hard minimum queue constraints.
"""

from __future__ import annotations

from typing import Any, Dict, List


def calculate_resilience_score(
    breakpoint_multiplier: float,
    overload_rate_at_moderate_stress: float,
    wait_escalation_ratio: float,
    staffing_buffer_ratio: float,
) -> Dict[str, Any]:
    """
    Calculate the 0–100 Branch Resilience Score deterministically.

    Parameters
    ----------
    breakpoint_multiplier:
        Calculated operational breakpoint (e.g. 1.72).
    overload_rate_at_moderate_stress:
        Fraction of time slots overloaded under 1.25x stress (0.0 to 1.0).
    wait_escalation_ratio:
        Ratio of wait time under 1.25x stress vs baseline (e.g. 1.5).
    staffing_buffer_ratio:
        Ratio of available staff buffer over minimum required staff (e.g. 0.33).

    Returns
    -------
    Dict with score (0-100), rating, and explainable contributing factors.
    """
    # 1. Demand Headroom score (40 points max)
    # Breakpoint 1.0x = 0 pts, 1.5x = 24 pts, 2.0x+ = 40 pts
    headroom_normalized = max(0.0, min(1.0, (breakpoint_multiplier - 1.0) / 1.0))
    headroom_pts = 40.0 * headroom_normalized

    if headroom_normalized >= 0.7:
        headroom_rating = "strong"
    elif headroom_normalized >= 0.4:
        headroom_rating = "moderate"
    else:
        headroom_rating = "critical"

    # 2. Overload Resistance (25 points max)
    # 0% overload = 25 pts, 100% overload = 0 pts
    overload_resistance = max(0.0, 1.0 - overload_rate_at_moderate_stress)
    overload_pts = 25.0 * overload_resistance

    if overload_resistance >= 0.8:
        overload_rating = "strong"
    elif overload_resistance >= 0.5:
        overload_rating = "moderate"
    else:
        overload_rating = "critical"

    # 3. Queue Stability (20 points max)
    # Escalation <= 1.2x wait = 20 pts, >= 4.0x = 0 pts
    stability_factor = max(0.0, min(1.0, (4.0 - wait_escalation_ratio) / (4.0 - 1.2)))
    stability_pts = 20.0 * stability_factor

    if stability_factor >= 0.7:
        stability_rating = "strong"
    elif stability_factor >= 0.4:
        stability_rating = "moderate"
    else:
        stability_rating = "critical"

    # 4. Workforce Flexibility (15 points max)
    # Buffer >= 0.30 = 15 pts, <= 0.05 = 0 pts
    flexibility_factor = max(0.0, min(1.0, staffing_buffer_ratio / 0.30))
    flexibility_pts = 15.0 * flexibility_factor

    if flexibility_factor >= 0.7:
        flexibility_rating = "strong"
    elif flexibility_factor >= 0.4:
        flexibility_rating = "moderate"
    else:
        flexibility_rating = "critical"

    total_score = round(headroom_pts + overload_pts + stability_pts + flexibility_pts, 0)
    total_score = max(5, min(98, int(total_score)))

    contributors = [
        {
            "factor": "Demand Headroom",
            "score": round(headroom_pts, 1),
            "max": 40,
            "rating": headroom_rating,
            "description": f"Stable operation sustained up to {breakpoint_multiplier:.2f}× baseline demand.",
        },
        {
            "factor": "Overload Resistance",
            "score": round(overload_pts, 1),
            "max": 25,
            "rating": overload_rating,
            "description": f"Overload incidence restricted to {overload_rate_at_moderate_stress * 100:.1f}% under moderate shock.",
        },
        {
            "factor": "Queue Stability",
            "score": round(stability_pts, 1),
            "max": 20,
            "rating": stability_rating,
            "description": f"Customer wait escalation ratio is {wait_escalation_ratio:.2f}× relative to baseline.",
        },
        {
            "factor": "Workforce Flexibility",
            "score": round(flexibility_pts, 1),
            "max": 15,
            "rating": flexibility_rating,
            "description": f"Staffing reallocation margin is {staffing_buffer_ratio * 100:.0f}% above queue minimums.",
        },
    ]

    return {
        "score": total_score,
        "max_score": 100,
        "contributors": contributors,
    }

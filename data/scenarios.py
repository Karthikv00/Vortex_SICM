"""
data/scenarios.py — Pre-defined ScenarioConfig instances.

Provides the three canonical scenarios (normal, peak, surge) with
fixed bank-branch queue definitions. All configuration lives here;
do not scatter magic numbers through other modules.

Implements: KARTHI-001 (scenario definitions)
Spec:        docs/architecture/data-model.md, docs/requirements/functional-requirements.md FR-DATA-1/2
"""

from __future__ import annotations

from backend.models import QueueConfig, ScenarioConfig

# ---------------------------------------------------------------------------
# Canonical queue catalogue — shared across all scenarios
# ---------------------------------------------------------------------------
# Three queues that represent a typical small bank branch:
#   Teller   — high-volume, short service time (cash/deposit)
#   Loans    — low-volume, long service time (loan enquiries)
#   Customer Service — medium-volume, medium service time (account issues)

_QUEUE_CATALOGUE = [
    QueueConfig(
        queue_id="teller",
        name="Teller",
        min_staff=1,
        max_staff=6,
        avg_service_time_minutes=4,
    ),
    QueueConfig(
        queue_id="loans",
        name="Loans",
        min_staff=1,
        max_staff=3,
        avg_service_time_minutes=15,
    ),
    QueueConfig(
        queue_id="customer_service",
        name="Customer Service",
        min_staff=1,
        max_staff=4,
        avg_service_time_minutes=8,
    ),
]

# Total staff available — same envelope for all scenarios so comparison is
# apples-to-apples (allocation changes, not budget changes).
_TOTAL_STAFF = 10


def normal_scenario(seed: int = 42) -> ScenarioConfig:
    """
    Normal weekday branch operation.
    Moderate, steady demand throughout the day with a mild lunch bump.
    Baseline staff allocation should be adequate without overload.
    """
    return ScenarioConfig(
        scenario_name="normal",
        seed=seed,
        horizon_start="09:00",
        horizon_end="17:00",
        slot_minutes=15,
        queues=_QUEUE_CATALOGUE,
        total_staff_available=_TOTAL_STAFF,
    )


def peak_scenario(seed: int = 42) -> ScenarioConfig:
    """
    Peak demand scenario (e.g. month-end or payday).
    Demand is roughly 1.5–2× normal during morning and early afternoon.
    Baseline staff shows moderate overload; optimized allocation resolves it.
    """
    return ScenarioConfig(
        scenario_name="peak",
        seed=seed,
        horizon_start="09:00",
        horizon_end="17:00",
        slot_minutes=15,
        queues=_QUEUE_CATALOGUE,
        total_staff_available=_TOTAL_STAFF,
    )


def surge_scenario(seed: int = 42) -> ScenarioConfig:
    """
    Surge scenario (e.g. festive season or special event).
    Demand spikes to 2.5–3× normal during peak hours (10:00–14:00).
    Baseline allocation is clearly insufficient; optimization demonstrates
    measurable improvement in wait time and overloaded slot reduction.
    """
    return ScenarioConfig(
        scenario_name="surge",
        seed=seed,
        horizon_start="09:00",
        horizon_end="17:00",
        slot_minutes=15,
        queues=_QUEUE_CATALOGUE,
        total_staff_available=_TOTAL_STAFF,
    )


# Registry for API / UI lookup
SCENARIO_REGISTRY: dict[str, callable] = {
    "normal": normal_scenario,
    "peak": peak_scenario,
    "surge": surge_scenario,
}


def get_scenario(scenario_name: str, seed: int = 42) -> ScenarioConfig:
    """
    Return a ScenarioConfig by name.

    Raises ValueError for unknown scenario names so callers get
    an explicit error rather than a silent None.
    """
    if scenario_name not in SCENARIO_REGISTRY:
        raise ValueError(
            f"Unknown scenario '{scenario_name}'. "
            f"Valid options: {list(SCENARIO_REGISTRY)}"
        )
    return SCENARIO_REGISTRY[scenario_name](seed=seed)

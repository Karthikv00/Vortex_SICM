"""REETHU-001: focused validation for synthetic scenario generation.

These tests intentionally exercise the public generator contract rather than
implementation details. The production generator is owned by Karthi and must
expose data.generator.generate(scenario_config).
"""

from copy import deepcopy

import pytest

from data.generator import generate


BASE_CONFIG = {
    "scenario_name": "normal",
    "seed": 42,
    "horizon_start": "09:00",
    "horizon_end": "17:00",
    "slot_minutes": 15,
    "queues": [
        {
            "queue_id": "teller",
            "name": "Teller",
            "min_staff": 1,
            "max_staff": 6,
            "avg_service_time_minutes": 4,
        },
        {
            "queue_id": "loans",
            "name": "Loans",
            "min_staff": 1,
            "max_staff": 3,
            "avg_service_time_minutes": 15,
        },
    ],
    "total_staff_available": 10,
}


def _arrival_data(result):
    """Read the generated arrival payload without depending on a concrete model."""
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif hasattr(result, "__dict__"):
        result = deepcopy(result.__dict__)

    for key in ("arrival_data", "arrivals", "generated_arrivals"):
        if key in result:
            return result[key]
    raise AssertionError("Generator result must expose generated arrival data")


def _scenario(config, name):
    scenario = deepcopy(config)
    scenario["scenario_name"] = name
    return scenario


def _flatten_counts(arrivals):
    if isinstance(arrivals, dict):
        values = arrivals.values()
    else:
        values = arrivals

    flattened = []
    for value in values:
        if isinstance(value, dict):
            flattened.extend(_flatten_counts(value))
        elif isinstance(value, (list, tuple)):
            flattened.extend(_flatten_counts(value))
        else:
            flattened.append(value)
    return flattened


def test_same_seed_and_scenario_are_deterministic():
    first = generate(deepcopy(BASE_CONFIG))
    second = generate(deepcopy(BASE_CONFIG))

    assert _arrival_data(first) == _arrival_data(second)


def test_surge_has_higher_arrival_demand_than_normal():
    normal = generate(_scenario(BASE_CONFIG, "normal"))
    surge = generate(_scenario(BASE_CONFIG, "surge"))

    normal_total = sum(_flatten_counts(_arrival_data(normal)))
    surge_total = sum(_flatten_counts(_arrival_data(surge)))

    assert surge_total > normal_total


def test_generation_covers_every_horizon_slot():
    result = generate(deepcopy(BASE_CONFIG))
    arrivals = _arrival_data(result)

    # Contract: every queue must have one value for every 15-minute slot.
    expected_slots = (17 - 9) * 60 // BASE_CONFIG["slot_minutes"]
    assert expected_slots == 32

    assert set(arrivals) == {q["queue_id"] for q in BASE_CONFIG["queues"]}
    for queue_id in arrivals:
        assert len(arrivals[queue_id]) == expected_slots


def test_generated_arrivals_are_non_negative():
    result = generate(deepcopy(BASE_CONFIG))
    counts = _flatten_counts(_arrival_data(result))

    assert counts
    assert all(isinstance(value, (int, float)) for value in counts)
    assert all(value >= 0 for value in counts)


@pytest.mark.parametrize("scenario", ["normal", "peak", "surge"])
def test_supported_scenarios_are_seed_reproducible(scenario):
    config = _scenario(BASE_CONFIG, scenario)

    first = generate(deepcopy(config))
    second = generate(deepcopy(config))

    assert _arrival_data(first) == _arrival_data(second)

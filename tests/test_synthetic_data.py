import pytest

from backend.synthetic_data import QueueConfig, ScenarioConfig, generate_arrivals


QUEUES = (
    QueueConfig("teller", 5.0),
    QueueConfig("loans", 1.5),
)


def config(scenario="normal", seed=42):
    return ScenarioConfig(scenario_name=scenario, seed=seed, queues=QUEUES)


def test_same_seed_is_reproducible():
    assert generate_arrivals(config(seed=7)) == generate_arrivals(config(seed=7))


def test_different_seed_changes_generated_data():
    assert generate_arrivals(config(seed=7)) != generate_arrivals(config(seed=8))


def test_expected_shape_for_09_to_17_with_15_minute_slots():
    arrivals = generate_arrivals(config())
    assert set(arrivals) == {"teller", "loans"}
    assert len(arrivals["teller"]) == 32
    assert len(arrivals["loans"]) == 32
    assert all(isinstance(value, int) and value >= 0 for values in arrivals.values() for value in values)


def test_scenarios_have_distinct_demand_intensity():
    normal = generate_arrivals(config("normal", 123))["teller"]
    peak = generate_arrivals(config("peak", 123))["teller"]
    surge = generate_arrivals(config("surge", 123))["teller"]
    assert sum(normal) < sum(peak) < sum(surge)


def test_invalid_scenario_is_rejected():
    with pytest.raises(ValueError, match="scenario_name"):
        generate_arrivals(ScenarioConfig(scenario_name="invalid", seed=1, queues=QUEUES))  # type: ignore[arg-type]


def test_empty_queues_are_rejected():
    with pytest.raises(ValueError, match="at least one queue"):
        generate_arrivals(ScenarioConfig(scenario_name="normal", seed=1))

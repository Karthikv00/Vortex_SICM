"""REETHU-001: Test scaffolding and generator test suite.

Validates the synthetic customer arrival generator against the documented contract:
- FR-DATA-1: Generate synthetic arrivals per queue per slot for a configurable day.
- FR-DATA-2: Support normal, peak, surge with distinct demand profiles.
- FR-DATA-3: Reproducible output given a fixed random seed (TC-01).
- FR-DATA-4: Standalone testability independent of API/UI.
- Acceptance Criteria & Test Cases: TC-01 (determinism), TC-02 (surge > normal), TC-03 (horizon coverage).

Target interface:
  data.generator.generate(scenario: ScenarioConfig | dict) -> ForecastResult
  data.generator.generate_arrivals(scenario: ScenarioConfig | dict) -> Dict[str, List[int]]
  data.generator.generate_slot_labels(scenario: ScenarioConfig | dict) -> List[str]
  data.scenarios.get_scenario(name: str, seed: int) -> ScenarioConfig
  backend.models.ScenarioConfig  — Literal["normal", "peak", "surge"] scenario_name
  backend.models.ForecastResult  — expected_arrivals: Dict[str, List[float]]
"""

from copy import deepcopy
from typing import Any, Dict, List

import pytest
from pydantic import ValidationError

from backend.models import ForecastResult, ScenarioConfig
from data.generator import generate, generate_arrivals, generate_slot_labels
from data.scenarios import get_scenario, normal_scenario, peak_scenario, surge_scenario


# ---------------------------------------------------------------------------
# Minimal test config — 2 queues, valid for the contract.
# Does NOT need to match the canonical 3-queue production config.
# ---------------------------------------------------------------------------
BASE_CONFIG: Dict[str, Any] = {
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


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _arrival_data(result: Any) -> Dict[str, List[float]]:
    """Extract the arrival mapping (queue_id -> list of counts) from a result object or dict."""
    if hasattr(result, "expected_arrivals"):
        return result.expected_arrivals
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif hasattr(result, "__dict__"):
        result = deepcopy(result.__dict__)

    for key in ("expected_arrivals", "arrival_data", "arrivals", "generated_arrivals"):
        if key in result:
            return result[key]
    raise AssertionError("Generator result must expose generated arrival data")


def _scenario_name(result: Any) -> str:
    """Extract scenario_name from a result object or dict."""
    if hasattr(result, "scenario_name"):
        return result.scenario_name
    if isinstance(result, dict) and "scenario_name" in result:
        return result["scenario_name"]
    raise AssertionError("Generator result must expose scenario_name")


def _slots(result: Any) -> List[str]:
    """Extract slot labels from a result object or dict."""
    if hasattr(result, "slots"):
        return result.slots
    if isinstance(result, dict) and "slots" in result:
        return result["slots"]
    raise AssertionError("Generator result must expose slots")


def _scenario_dict(config: Dict[str, Any], name: str) -> Dict[str, Any]:
    scenario = deepcopy(config)
    scenario["scenario_name"] = name
    return scenario


def _flatten_counts(arrivals: Any) -> List[float]:
    if isinstance(arrivals, dict):
        values = arrivals.values()
    else:
        values = arrivals

    flattened: List[float] = []
    for value in values:
        if isinstance(value, dict):
            flattened.extend(_flatten_counts(value))
        elif isinstance(value, (list, tuple)):
            flattened.extend(_flatten_counts(value))
        else:
            flattened.append(float(value))
    return flattened


# ===========================================================================
# 1. NORMAL / PEAK / SURGE
#    - valid supported scenarios are accepted
#    - generated results identify the correct scenario
# ===========================================================================

@pytest.mark.parametrize("scenario_name", ["normal", "peak", "surge"])
def test_supported_scenarios_accepted_and_identified(scenario_name: str):
    """Supported scenarios (normal, peak, surge) are accepted and identify the scenario."""
    # Test with dict configuration
    config = _scenario_dict(BASE_CONFIG, scenario_name)
    res_dict = generate(config)
    assert _scenario_name(res_dict) == scenario_name

    # Test with domain model ScenarioConfig
    canonical_cfg = get_scenario(scenario_name, seed=42)
    res_model = generate(canonical_cfg)
    assert _scenario_name(res_model) == scenario_name


# ===========================================================================
# 2. DETERMINISM
#    - identical configuration + identical seed produces identical output
# ===========================================================================

def test_same_seed_and_scenario_are_deterministic():
    """Identical configuration + identical seed produces identical arrival output."""
    first = generate(deepcopy(BASE_CONFIG))
    second = generate(deepcopy(BASE_CONFIG))

    assert _arrival_data(first) == _arrival_data(second)
    assert _slots(first) == _slots(second)


@pytest.mark.parametrize("scenario_name", ["normal", "peak", "surge"])
def test_all_supported_scenarios_are_deterministic(scenario_name: str):
    """Determinism holds across all canonical scenarios with fixed seed."""
    cfg1 = get_scenario(scenario_name, seed=123)
    cfg2 = get_scenario(scenario_name, seed=123)

    first = generate(cfg1)
    second = generate(cfg2)

    assert _arrival_data(first) == _arrival_data(second)


# ===========================================================================
# 3. DEMAND BEHAVIOR
#    - surge demand is higher than normal according to documented behavior
#    - peak demand is higher than normal (documented multiplier ordering)
#    - do not invent numerical thresholds that are not specified by project
# ===========================================================================

def test_surge_demand_is_higher_than_normal():
    """Surge scenario produces higher total demand and higher peak slot arrivals than normal."""
    normal = generate(_scenario_dict(BASE_CONFIG, "normal"))
    surge = generate(_scenario_dict(BASE_CONFIG, "surge"))

    normal_arrivals = _arrival_data(normal)
    surge_arrivals = _arrival_data(surge)

    normal_total = sum(_flatten_counts(normal_arrivals))
    surge_total = sum(_flatten_counts(surge_arrivals))

    # Overall volume in surge must exceed normal
    assert surge_total > normal_total, f"Surge total ({surge_total}) must be > normal ({normal_total})"

    # Acceptance criteria / TC-02: surge has higher arrival rate than normal in at least one window/slot
    has_higher_slot = any(
        any(s > n for s, n in zip(surge_arrivals[qid], normal_arrivals[qid]))
        for qid in normal_arrivals
    )
    assert has_higher_slot, "Surge arrivals must exceed normal in at least one slot"


def test_peak_demand_is_higher_than_normal():
    """Peak scenario produces higher total demand than normal (multiplier: 1.7 vs 1.0)."""
    normal = generate(_scenario_dict(BASE_CONFIG, "normal"))
    peak = generate(_scenario_dict(BASE_CONFIG, "peak"))

    normal_total = sum(_flatten_counts(_arrival_data(normal)))
    peak_total = sum(_flatten_counts(_arrival_data(peak)))

    assert peak_total > normal_total, (
        f"Peak total ({peak_total}) must be > normal ({normal_total})"
    )


def test_demand_ordering_normal_peak_surge():
    """Documented demand intensity ordering: normal < peak < surge (canonical 3-queue config)."""
    normal = generate(normal_scenario(seed=42))
    peak = generate(peak_scenario(seed=42))
    surge = generate(surge_scenario(seed=42))

    normal_total = sum(_flatten_counts(_arrival_data(normal)))
    peak_total = sum(_flatten_counts(_arrival_data(peak)))
    surge_total = sum(_flatten_counts(_arrival_data(surge)))

    assert normal_total < peak_total, (
        f"normal ({normal_total}) must be < peak ({peak_total})"
    )
    assert peak_total < surge_total, (
        f"peak ({peak_total}) must be < surge ({surge_total})"
    )


# ===========================================================================
# 4. TIME HORIZON
#    - output contains the required 15-minute slots
#    - verify the documented 09:00-17:00 horizon
#    - follow the repository's actual interpretation of the end time
# ===========================================================================

def test_generation_covers_documented_time_horizon():
    """09:00-17:00 horizon with 15-minute slots yields 32 slots from 09:00 to 16:45."""
    result = generate(deepcopy(BASE_CONFIG))
    slots = _slots(result)
    arrivals = _arrival_data(result)

    expected_slot_count = (17 - 9) * 60 // BASE_CONFIG["slot_minutes"]
    assert expected_slot_count == 32
    assert len(slots) == expected_slot_count

    # Repository interpretation of 09:00-17:00: slots start at 09:00 and end at 16:45 (last 15m period)
    assert slots[0] == "09:00"
    assert slots[-1] == "16:45"

    # Verify each queue has exactly one arrival count per slot
    expected_queues = {q["queue_id"] for q in BASE_CONFIG["queues"]}
    assert set(arrivals.keys()) == expected_queues
    for queue_id in arrivals:
        assert len(arrivals[queue_id]) == expected_slot_count


def test_slot_labels_helper_matches_horizon():
    """generate_slot_labels correctly formats 15-minute intervals."""
    labels = generate_slot_labels(BASE_CONFIG)
    assert len(labels) == 32
    assert labels[0] == "09:00"
    assert labels[1] == "09:15"
    assert labels[-1] == "16:45"


def test_slot_labels_are_hhmm_format():
    """All slot labels are formatted as HH:MM with zero-padded hours and minutes."""
    labels = generate_slot_labels(BASE_CONFIG)
    for label in labels:
        assert len(label) == 5, f"Slot label '{label}' is not 5 chars"
        assert label[2] == ":", f"Slot label '{label}' missing colon at index 2"
        h, m = label.split(":")
        assert h.isdigit() and len(h) == 2, f"Hour part '{h}' not zero-padded"
        assert m.isdigit() and len(m) == 2, f"Minute part '{m}' not zero-padded"
        assert 0 <= int(h) <= 23 and int(m) in (0, 15, 30, 45), (
            f"Unexpected slot label '{label}' for 15-minute slots"
        )


# ===========================================================================
# 5. DATA VALIDITY
#    - arrival counts are never negative
#    - output follows the documented ForecastResult / data structure
#    - ForecastResult.expected_arrivals values are float (per models.py contract)
#    - generate_arrivals (raw helper) returns int per its docstring
# ===========================================================================

def test_generated_arrivals_are_non_negative():
    """Arrival counts across all queues and slots must be non-negative."""
    result = generate(deepcopy(BASE_CONFIG))
    counts = _flatten_counts(_arrival_data(result))

    assert len(counts) > 0
    assert all(isinstance(val, (int, float)) for val in counts)
    assert all(val >= 0 for val in counts)


def test_output_conforms_to_forecast_result_contract():
    """Generated result adheres to the ForecastResult contract structure."""
    result = generate(deepcopy(BASE_CONFIG))

    # The generator returns a ForecastResult instance
    assert isinstance(result, ForecastResult), (
        f"generate() must return ForecastResult, got {type(result).__name__}"
    )
    assert isinstance(result.scenario_name, str)
    assert isinstance(result.slots, list)
    assert isinstance(result.expected_arrivals, dict)

    slots = _slots(result)
    arrivals = _arrival_data(result)
    for qid, counts in arrivals.items():
        assert len(counts) == len(slots), f"Queue {qid} counts length does not match slots"


def test_forecast_result_expected_arrivals_are_float():
    """ForecastResult.expected_arrivals contains float values per the models.py contract.

    generate() casts generate_arrivals() int counts to float before returning.
    """
    result = generate(deepcopy(BASE_CONFIG))
    arrivals = _arrival_data(result)

    for qid, counts in arrivals.items():
        for val in counts:
            assert isinstance(val, float), (
                f"Queue {qid}: expected float in ForecastResult.expected_arrivals, got {type(val).__name__} ({val})"
            )


def test_generate_arrivals_returns_int_counts():
    """generate_arrivals() (raw helper) returns integer arrival counts per its docstring.

    Arrival counts must be non-negative integers before the float cast in generate().
    """
    from data.scenarios import normal_scenario as ns
    arrivals = generate_arrivals(ns(seed=42))

    assert isinstance(arrivals, dict)
    for qid, counts in arrivals.items():
        assert isinstance(counts, list), f"Queue {qid}: expected list, got {type(counts).__name__}"
        for val in counts:
            assert isinstance(val, int), (
                f"Queue {qid}: generate_arrivals must return int counts, got {type(val).__name__} ({val})"
            )
            assert val >= 0, f"Queue {qid}: negative count {val}"


def test_canonical_three_queue_config_produces_all_queues():
    """The canonical production config (3 queues) generates arrivals for all three queues."""
    cfg = normal_scenario(seed=42)
    result = generate(cfg)

    expected_queues = {"teller", "loans", "customer_service"}
    assert set(result.expected_arrivals.keys()) == expected_queues, (
        f"Expected queues {expected_queues}, got {set(result.expected_arrivals.keys())}"
    )
    for qid in expected_queues:
        assert len(result.expected_arrivals[qid]) == 32, (
            f"Queue {qid}: expected 32 slots, got {len(result.expected_arrivals[qid])}"
        )
        assert all(v >= 0 for v in result.expected_arrivals[qid]), (
            f"Queue {qid}: negative arrivals found"
        )


# ===========================================================================
# 6. SEED VARIATION
#    - different seeds produce different deterministic results where variation is permitted
# ===========================================================================

def test_different_seeds_produce_different_arrivals():
    """Different random seeds produce distinct deterministic arrival sequences."""
    cfg_seed_1 = deepcopy(BASE_CONFIG)
    cfg_seed_1["seed"] = 42

    cfg_seed_2 = deepcopy(BASE_CONFIG)
    cfg_seed_2["seed"] = 999

    res_1 = generate(cfg_seed_1)
    res_2 = generate(cfg_seed_2)

    assert _arrival_data(res_1) != _arrival_data(res_2)


# ===========================================================================
# 7. INVALID INPUT
#    - invalid scenario names are rejected if project's contract specifies validation
#    - get_scenario() raises ValueError (registry path)
#    - ScenarioConfig() raises ValidationError (Pydantic Literal path)
#    - generate(dict) raises ValidationError via ScenarioConfig(**dict) conversion
# ===========================================================================

def test_invalid_scenario_name_rejected():
    """Passing an invalid scenario name raises validation error per contract."""
    invalid_cfg = deepcopy(BASE_CONFIG)
    invalid_cfg["scenario_name"] = "unsupported_scenario"

    with pytest.raises((ValidationError, ValueError)):
        generate(invalid_cfg)


def test_invalid_scenario_model_rejected():
    """Constructing ScenarioConfig with invalid scenario name raises ValidationError."""
    with pytest.raises(ValidationError):
        ScenarioConfig(
            scenario_name="invalid_scenario",
            seed=42,
            horizon_start="09:00",
            horizon_end="17:00",
            slot_minutes=15,
            queues=BASE_CONFIG["queues"],
            total_staff_available=10,
        )


def test_get_scenario_raises_value_error_for_unknown_name():
    """get_scenario() raises ValueError (not ValidationError) for an unknown name.

    The registry path in data.scenarios explicitly raises ValueError before
    ScenarioConfig construction, so callers can distinguish lookup errors from
    schema errors.
    """
    with pytest.raises(ValueError, match="normal|peak|surge"):
        get_scenario("weekend_rush", seed=42)

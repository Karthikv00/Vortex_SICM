"""
tests/test_data.py — Data generator tests.

Covers: TC-01 (determinism), TC-02 (surge > normal), TC-03 (full horizon).
REETHU-001.
"""
from __future__ import annotations

from data.generator import generate, generate_slot_labels
from data.scenarios import get_scenario, normal_scenario, surge_scenario


def test_determinism_tc01():
    """TC-01: Same seed + scenario → identical output."""
    r1 = generate(normal_scenario(seed=42))
    r2 = generate(normal_scenario(seed=42))
    assert r1.expected_arrivals == r2.expected_arrivals


def test_different_seeds_differ():
    r1 = generate(normal_scenario(seed=42))
    r2 = generate(normal_scenario(seed=99))
    # With different seeds the outputs should differ
    assert r1.expected_arrivals != r2.expected_arrivals


def test_surge_greater_than_normal_tc02():
    """TC-02: Surge peak arrival rate > normal in at least one slot."""
    norm = generate(normal_scenario(seed=42))
    surge = generate(surge_scenario(seed=42))
    # Check teller queue — should have at least one slot where surge > normal
    norm_teller = norm.expected_arrivals["teller"]
    surge_teller = surge.expected_arrivals["teller"]
    assert any(s > n for s, n in zip(surge_teller, norm_teller)), \
        "Surge should exceed normal in at least one slot"


def test_full_horizon_coverage_tc03():
    """TC-03: Generated data covers every horizon slot."""
    cfg = normal_scenario(seed=42)
    result = generate(cfg)
    expected_slots = cfg.slot_count()
    assert len(result.slots) == expected_slots
    for qid, arrivals in result.expected_arrivals.items():
        assert len(arrivals) == expected_slots, f"Queue {qid} has wrong slot count"


def test_all_arrivals_non_negative():
    """All generated arrival counts must be >= 0."""
    for scenario_name in ["normal", "peak", "surge"]:
        cfg = get_scenario(scenario_name, seed=42)
        result = generate(cfg)
        for qid, arrivals in result.expected_arrivals.items():
            assert all(v >= 0 for v in arrivals), f"Negative arrivals in {scenario_name}/{qid}"


def test_slot_labels_format():
    cfg = normal_scenario(seed=42)
    labels = generate_slot_labels(cfg)
    assert labels[0] == "09:00"
    assert labels[-1] == "16:45"
    assert len(labels) == 32

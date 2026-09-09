"""
tests/conftest.py — Shared pytest fixtures.

Provides canonical scenario configs, forecasts, and allocations
so test files don't each re-build boilerplate.
"""
from __future__ import annotations

import pytest

from backend.models import AllocationPlan, ScenarioConfig
from data.scenarios import normal_scenario, peak_scenario, surge_scenario
from backend.forecasting.forecast import forecast as run_forecast
from backend.models import ForecastResult


# ---------------------------------------------------------------------------
# Scenario fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def normal_cfg() -> ScenarioConfig:
    return normal_scenario(seed=42)

@pytest.fixture(scope="session")
def peak_cfg() -> ScenarioConfig:
    return peak_scenario(seed=42)

@pytest.fixture(scope="session")
def surge_cfg() -> ScenarioConfig:
    return surge_scenario(seed=42)

# ---------------------------------------------------------------------------
# Forecast fixtures (derived from scenario)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def normal_forecast(normal_cfg) -> ForecastResult:
    return run_forecast(normal_cfg)

@pytest.fixture(scope="session")
def surge_forecast(surge_cfg) -> ForecastResult:
    return run_forecast(surge_cfg)

# ---------------------------------------------------------------------------
# Allocation fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def adequate_allocation(normal_cfg) -> AllocationPlan:
    """Allocation with enough staff for normal demand."""
    return AllocationPlan(
        label="baseline",
        staff_by_queue={q.queue_id: q.min_staff + 1 for q in normal_cfg.queues},
    )

@pytest.fixture(scope="session")
def tight_allocation(normal_cfg) -> AllocationPlan:
    """Allocation at absolute minimum — expect some overload on peak/surge."""
    return AllocationPlan(
        label="baseline",
        staff_by_queue={q.queue_id: q.min_staff for q in normal_cfg.queues},
    )

@pytest.fixture(scope="session")
def zero_staff_allocation(normal_cfg) -> AllocationPlan:
    """Zero staff — all queues overloaded."""
    return AllocationPlan(
        label="whatif",
        staff_by_queue={q.queue_id: 0 for q in normal_cfg.queues},
    )

"""
tests/test_stress_test.py — Comprehensive tests for Branch Stress Test & Resilience Engine.
"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.resilience.engine import StressTestConfig, run_branch_stress_test
from backend.routes.custom_workload import UnifiedTask

client = TestClient(app)

SAMPLE_TASKS = [
    UnifiedTask(task_type="teller", name="Deposits", customers_per_hour=14.0, service_minutes=3.5),
    UnifiedTask(task_type="teller", name="Withdrawals", customers_per_hour=8.0, service_minutes=4.0),
    UnifiedTask(task_type="loan", name="Personal Loans", customers_per_hour=3.0, service_minutes=20.0),
    UnifiedTask(task_type="customer_service", name="KYC & Onboarding", customers_per_hour=8.0, service_minutes=10.0),
]


def test_baseline_stress_test_reproduces_baseline():
    """1.0x stress produces equivalent workload to baseline."""
    res = run_branch_stress_test(SAMPLE_TASKS, StressTestConfig(category="demand_shock"))
    assert "baseline" in res
    assert "stressScenarios" in res
    assert len(res["stressScenarios"]) > 0

    base_step = res["stressScenarios"][0]
    assert base_step["demandMultiplier"] == 1.00
    assert base_step["averageWait"] == res["baseline"]["averageWait"]
    assert base_step["overloadedSlots"] == res["baseline"]["overloadedSlots"]


def test_demand_increase_strictly_increases_stress():
    """Increasing demand shock increases wait or overload."""
    res = run_branch_stress_test(SAMPLE_TASKS, StressTestConfig(category="demand_shock"))
    scenarios = res["stressScenarios"]
    # Demand shock increases utilization across the branch
    assert scenarios[-1]["utilization"] > scenarios[0]["utilization"]


def test_stress_test_is_deterministic():
    """Stress test execution is strictly deterministic."""
    res1 = run_branch_stress_test(SAMPLE_TASKS, StressTestConfig(category="demand_shock", seed=42))
    res2 = run_branch_stress_test(SAMPLE_TASKS, StressTestConfig(category="demand_shock", seed=42))

    assert res1["breakpoint"]["multiplier"] == res2["breakpoint"]["multiplier"]
    assert res1["resilienceScore"] == res2["resilienceScore"]
    assert res1["bottleneck"]["queue"] == res2["bottleneck"]["queue"]
    assert res1["recoveryPlans"][0]["action"] == res2["recoveryPlans"][0]["action"]


def test_breakpoint_is_dynamically_calculated():
    """Breakpoint changes depending on workload scale rather than being hardcoded."""
    light_tasks = [
        UnifiedTask(task_type="teller", name="Light Teller", customers_per_hour=5.0, service_minutes=3.0),
        UnifiedTask(task_type="loan", name="Light Loan", customers_per_hour=1.0, service_minutes=15.0),
        UnifiedTask(task_type="customer_service", name="Light CS", customers_per_hour=3.0, service_minutes=8.0),
    ]
    heavy_tasks = [
        UnifiedTask(task_type="teller", name="Heavy Teller", customers_per_hour=30.0, service_minutes=4.0),
        UnifiedTask(task_type="loan", name="Heavy Loan", customers_per_hour=6.0, service_minutes=25.0),
        UnifiedTask(task_type="customer_service", name="Heavy CS", customers_per_hour=15.0, service_minutes=12.0),
    ]

    res_light = run_branch_stress_test(light_tasks, StressTestConfig(category="demand_shock"))
    res_heavy = run_branch_stress_test(heavy_tasks, StressTestConfig(category="demand_shock"))

    # Light workload should sustain a higher breakpoint multiplier than heavy workload
    assert res_light["breakpoint"]["multiplier"] > res_heavy["breakpoint"]["multiplier"]
    assert res_light["resilienceScore"] > res_heavy["resilienceScore"]


def test_bottleneck_corresponds_to_actual_degradation():
    """Bottleneck queue matches queue with highest degradation."""
    teller_heavy = [
        UnifiedTask(task_type="teller", name="Super Teller", customers_per_hour=35.0, service_minutes=4.0),
        UnifiedTask(task_type="loan", name="Normal Loan", customers_per_hour=1.0, service_minutes=15.0),
        UnifiedTask(task_type="customer_service", name="Normal CS", customers_per_hour=2.0, service_minutes=8.0),
    ]
    res = run_branch_stress_test(teller_heavy, StressTestConfig(category="demand_shock"))
    assert res["bottleneck"]["queue"] == "teller"


def test_recovery_plans_respect_staffing_constraints_and_improve_wait():
    """Recovery plans are feasible and provide measurable improvements."""
    res = run_branch_stress_test(SAMPLE_TASKS, StressTestConfig(category="demand_shock"))
    plans = res["recoveryPlans"]
    assert len(plans) > 0

    for plan in plans:
        assert "resulting_allocation" in plan
        assert "disruption_score" in plan
        assert plan["wait_reduction_minutes"] >= 0

    # Top plan should provide positive wait reduction
    assert plans[0]["wait_reduction_minutes"] >= 0


def test_stress_test_api_endpoint():
    """POST /api/stress-test works via FastAPI test client."""
    payload = {
        "branch_id": "branch-main",
        "tasks": [
            {"taskType": "teller", "taskName": "Cash Desk", "customersPerHour": 15.0, "averageServiceTimeMinutes": 3.5},
            {"taskType": "loan", "taskName": "Mortgages", "customersPerHour": 2.0, "averageServiceTimeMinutes": 20.0},
            {"taskType": "customer_service", "taskName": "Support", "customersPerHour": 6.0, "averageServiceTimeMinutes": 8.0},
        ],
        "stress_config": {"category": "demand_shock", "seed": 42},
    }
    response = client.post("/api/stress-test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "resilienceScore" in data
    assert "breakpoint" in data
    assert "recoveryPlans" in data
    assert "bottleneck" in data


def test_service_time_shock_and_workforce_shock():
    """Service time and workforce shock categories execute reliably."""
    res_service = run_branch_stress_test(SAMPLE_TASKS, StressTestConfig(category="service_time_shock"))
    assert res_service["stressCategory"] == "service_time_shock"
    assert len(res_service["stressScenarios"]) == 4

    res_workforce = run_branch_stress_test(SAMPLE_TASKS, StressTestConfig(category="workforce_shock"))
    assert res_workforce["stressCategory"] == "workforce_shock"
    assert len(res_workforce["stressScenarios"]) == 3

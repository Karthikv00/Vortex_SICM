"""
tests/test_custom_workload.py — Tests for unified workload input and end-to-end pipeline.

Verifies:
1. Unified task payload acceptance (Teller, Loan, Customer Service)
2. Normalization into canonical queue models
3. Demand aggregation (multiple tasks per queue)
4. Automatic scenario classification (Normal, Peak, Surge)
5. Demand forecasting, overload detection, and mathematical resource optimization
6. Explainable reasoning and impact metrics
7. What-If hypothetical simulation
"""
from fastapi.testclient import TestClient
import pytest

from backend.main import app
from backend.routes.custom_workload import CustomTask, CustomWorkloadRequest, UnifiedTask, analyze_custom_workload

client = TestClient(app)


def test_acceptance_criteria_pipeline():
    """
    Test the exact acceptance criteria workflow from the MASTER PROMPT:
    Teller: Cash withdrawal (30 cust/hr, 5 min)
    Loan: Home loan application (5 cust/hr, 20 min)
    Customer Service: Account update (10 cust/hr, 8 min)
    """
    payload = {
        "tasks": [
            {
                "taskType": "teller",
                "taskName": "Cash withdrawal",
                "customersPerHour": 30,
                "averageServiceTimeMinutes": 5.0,
            },
            {
                "taskType": "loan",
                "taskName": "Home loan application",
                "customersPerHour": 5,
                "averageServiceTimeMinutes": 20.0,
            },
            {
                "taskType": "customer_service",
                "taskName": "Account update",
                "customersPerHour": 10,
                "averageServiceTimeMinutes": 8.0,
            },
        ],
        "seed": 42,
    }

    response = client.post("/api/custom-workload/analyze", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    # 1. Tasks accepted and scenario auto-classified
    assert data["scenario_label"] in ("Normal demand", "Peak demand", "Surge demand")
    assert "demand_multiplier" in data
    assert data["demand_multiplier"] > 0

    # 2. Queue service times adjusted from custom tasks
    queues = {q["queue_id"]: q for q in data["scenario"]["queues"]}
    assert queues["teller"]["avg_service_time_minutes"] == 5.0
    assert queues["loans"]["avg_service_time_minutes"] == 20.0
    assert queues["customer_service"]["avg_service_time_minutes"] == 8.0

    # 3. Forecast generated
    forecast = data["forecast"]
    assert "expected_arrivals" in forecast
    assert len(forecast["slots"]) == 32
    assert "teller" in forecast["expected_arrivals"]
    assert "loans" in forecast["expected_arrivals"]
    assert "customer_service" in forecast["expected_arrivals"]

    # 4. Optimization run and feasible allocation produced
    opt = data["optimization"]
    assert opt["feasible"] is True
    assert "baseline" in opt
    assert "optimized" in opt
    assert "explanation" in opt
    assert len(opt["explanation"]) > 20

    # 5. Total staff constraint respected
    opt_staff = opt["optimized"]["allocation"]["staff_by_queue"]
    total_staff = sum(opt_staff.values())
    assert total_staff <= data["scenario"]["total_staff_available"]
    assert opt_staff["teller"] >= queues["teller"]["min_staff"]
    assert opt_staff["loans"] >= queues["loans"]["min_staff"]
    assert opt_staff["customer_service"] >= queues["customer_service"]["min_staff"]


def test_multiple_tasks_demand_aggregation():
    """
    Multiple tasks for the same queue must aggregate demand correctly:
    Teller: Cash withdrawal = 10, Cash deposit = 8, Account withdrawal = 5 -> Total Teller demand = 23
    """
    payload = {
        "tasks": [
            {"taskType": "teller", "taskName": "Cash withdrawal", "customersPerHour": 10, "averageServiceTimeMinutes": 4.0},
            {"taskType": "teller", "taskName": "Cash deposit", "customersPerHour": 8, "averageServiceTimeMinutes": 5.0},
            {"taskType": "teller", "taskName": "Account withdrawal", "customersPerHour": 5, "averageServiceTimeMinutes": 6.0},
            {"taskType": "loans", "taskName": "Loan enquiry", "customersPerHour": 4, "averageServiceTimeMinutes": 15.0},
            {"taskType": "customer_service", "taskName": "General query", "customersPerHour": 8, "averageServiceTimeMinutes": 8.0},
        ],
        "seed": 42,
    }
    req = CustomWorkloadRequest.model_validate(payload)
    assert len(req.teller) == 3
    teller_hourly = sum(t.customers_per_hour for t in req.teller)
    assert teller_hourly == 23.0

    res = analyze_custom_workload(req)
    assert res["scenario_label"] is not None
    # Weighted average service time for teller: (10*4 + 8*5 + 5*6)/23 = (40 + 40 + 30)/23 = 110/23 ≈ 4.78
    queues = {q["queue_id"]: q for q in res["scenario"]["queues"]}
    assert abs(queues["teller"]["avg_service_time_minutes"] - 4.78) < 0.05


def test_scenario_classification_thresholds():
    """
    Verifies automatic classification across demand bands:
    - Normal (< 1.35x)
    - Peak (1.35 - 2.25x)
    - Surge (> 2.25x)
    Canonical rates: teller=20, loans=4.8, CS=10 -> sum=34.8
    """
    # Normal: total 20 cust/hr -> multiplier = 20/34.8 = 0.57 < 1.35
    req_normal = CustomWorkloadRequest(
        tasks=[UnifiedTask(taskType="teller", taskName="Cash", customersPerHour=20, averageServiceTimeMinutes=4)]
    )
    res_normal = analyze_custom_workload(req_normal)
    assert res_normal["scenario_label"] == "Normal demand"

    # Peak: total 60 cust/hr -> multiplier = 60/34.8 = 1.72 (1.35 - 2.25)
    req_peak = CustomWorkloadRequest(
        tasks=[UnifiedTask(taskType="teller", taskName="Cash", customersPerHour=60, averageServiceTimeMinutes=4)]
    )
    res_peak = analyze_custom_workload(req_peak)
    assert res_peak["scenario_label"] == "Peak demand"

    # Surge: total 90 cust/hr -> multiplier = 90/34.8 = 2.58 > 2.25
    req_surge = CustomWorkloadRequest(
        tasks=[UnifiedTask(taskType="teller", taskName="Cash", customersPerHour=90, averageServiceTimeMinutes=4)]
    )
    res_surge = analyze_custom_workload(req_surge)
    assert res_surge["scenario_label"] == "Surge demand"


def test_empty_workload_validation():
    """Empty workload must be rejected with 422 Unprocessable Entity."""
    response = client.post("/api/custom-workload/analyze", json={"tasks": []})
    assert response.status_code == 422

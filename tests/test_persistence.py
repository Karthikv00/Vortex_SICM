"""
tests/test_persistence.py — Tests for Supabase persistence layer and branch/task endpoints.
"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.persistence import db

client = TestClient(app)


def test_persistence_status():
    """GET /api/persistence/status returns valid connectivity state."""
    response = client.get("/api/persistence/status")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert "mode" in data


def test_env_key_resolution_supports_all_casing_and_names(monkeypatch):
    """Supports supabase_url, anon_key, service_role_key in any letter case."""
    for k in ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY"]:
        monkeypatch.delenv(k, raising=False)

    monkeypatch.setenv("supabase_url", "https://xyz123.supabase.co")
    monkeypatch.setenv("anon_key", "mock-anon-key-abc")
    monkeypatch.setenv("service_role_key", "mock-service-role-key-xyz")

    db.reload_config(load_from_file=False)
    assert db.supabase_url == "https://xyz123.supabase.co"
    assert db.anon_key == "mock-anon-key-abc"
    assert db.service_role_key == "mock-service-role-key-xyz"
    # Service role key is preferred for server operations
    assert db.supabase_key == "mock-service-role-key-xyz"
    assert db.is_supabase_configured is True

    # If only anon_key is present, it is used
    monkeypatch.delenv("service_role_key", raising=False)
    monkeypatch.delenv("SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    db.reload_config(load_from_file=False)
    assert db.supabase_key == "mock-anon-key-abc"


def test_branch_list_and_create():
    """Branch creation and listing works."""
    # List branches
    response = client.get("/api/branches")
    assert response.status_code == 200
    branches = response.json()
    assert len(branches) >= 1
    assert any(b["id"] == "branch-main" for b in branches)

    # Create new branch
    create_res = client.post(
        "/api/branches",
        json={"name": "Uptown Branch", "location": "North Suburbs"},
    )
    assert create_res.status_code == 201
    new_b = create_res.json()
    assert new_b["name"] == "Uptown Branch"


def test_task_crud_lifecycle():
    """Branch tasks support full CRUD with validation."""
    branch_id = "branch-main"

    # 1. Create task
    task_payload = {
        "taskType": "loan",
        "taskName": "Commercial Loan Review",
        "customersPerHour": 2.5,
        "averageServiceTimeMinutes": 30.0,
    }
    create_res = client.post(f"/api/branches/{branch_id}/tasks", json=task_payload)
    assert create_res.status_code == 201
    created_task = create_res.json()
    task_id = created_task["id"]
    assert created_task["task_name"] == "Commercial Loan Review"

    # 2. Read tasks
    list_res = client.get(f"/api/branches/{branch_id}/tasks")
    assert list_res.status_code == 200
    tasks = list_res.json()
    assert any(t["id"] == task_id for t in tasks)

    # 3. Update task
    update_res = client.put(
        f"/api/branches/{branch_id}/tasks/{task_id}",
        json={"customersPerHour": 4.0},
    )
    assert update_res.status_code == 200
    updated_task = update_res.json()
    assert updated_task["customers_per_hour"] == 4.0

    # 4. Delete task
    del_res = client.delete(f"/api/branches/{branch_id}/tasks/{task_id}")
    assert del_res.status_code == 200

    # Verify deleted
    list_after = client.get(f"/api/branches/{branch_id}/tasks").json()
    assert not any(t["id"] == task_id for t in list_after)


def test_task_validation_rejects_invalid_inputs():
    """Invalid task inputs return 422 validation errors."""
    branch_id = "branch-main"

    # Invalid taskType
    res1 = client.post(
        f"/api/branches/{branch_id}/tasks",
        json={"taskType": "crypto", "taskName": "Trading", "customersPerHour": 1.0, "averageServiceTimeMinutes": 5.0},
    )
    assert res1.status_code == 422

    # Negative customers per hour
    res2 = client.post(
        f"/api/branches/{branch_id}/tasks",
        json={"taskType": "teller", "taskName": "Deposit", "customersPerHour": -5.0, "averageServiceTimeMinutes": 5.0},
    )
    assert res2.status_code == 422

    # Zero/negative service time
    res3 = client.post(
        f"/api/branches/{branch_id}/tasks",
        json={"taskType": "teller", "taskName": "Deposit", "customersPerHour": 5.0, "averageServiceTimeMinutes": 0.0},
    )
    assert res3.status_code == 422


def test_scenario_persistence_and_retrieval():
    """Scenario snapshots can be persisted and retrieved."""
    branch_id = "branch-main"
    payload = {
        "branch_id": branch_id,
        "scenario_type": "stress_test",
        "scenario_name": "Q3 Surge Stress Evaluation",
        "input_snapshot": {"multiplier": 1.5, "tasks_count": 4},
        "result_snapshot": {"resilienceScore": 82, "breakpoint": 1.72, "bottleneck": "Teller"},
    }

    save_res = client.post("/api/scenarios", json=payload)
    assert save_res.status_code == 201
    saved = save_res.json()
    assert saved["scenario_name"] == "Q3 Surge Stress Evaluation"
    assert "id" in saved

    # Retrieve scenario runs
    get_res = client.get(f"/api/branches/{branch_id}/scenarios?scenario_type=stress_test")
    assert get_res.status_code == 200
    runs = get_res.json()
    assert len(runs) >= 1
    assert any(r["id"] == saved["id"] for r in runs)

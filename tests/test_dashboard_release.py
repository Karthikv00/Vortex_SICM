from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_scenario_generate_includes_authoritative_baseline():
    response = client.post(
        "/api/scenario/generate",
        json={"scenario_name": "surge", "seed": 42},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["baseline"]["label"] == "baseline"
    assert payload["baseline"]["staff_by_queue"] == {
        "teller": 4,
        "loans": 3,
        "customer_service": 3,
    }


def test_scenario_baseline_endpoint_is_deterministic():
    generated = client.post(
        "/api/scenario/generate",
        json={"scenario_name": "peak", "seed": 42},
    )
    assert generated.status_code == 200
    scenario = generated.json()["scenario"]

    first = client.post("/api/scenario/baseline", json=scenario)
    second = client.post("/api/scenario/baseline", json=scenario)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert first.json()["label"] == "baseline"

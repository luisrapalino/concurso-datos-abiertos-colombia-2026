import pytest


@pytest.mark.integration
def test_territorial_boundaries_endpoint(client) -> None:
    response = client.get("/api/v1/territorial-boundaries", params={"level": "department"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "FeatureCollection"
    assert len(payload["features"]) >= 30


@pytest.mark.integration
def test_data_drift_endpoint(client) -> None:
    response = client.get("/api/v1/data-drift")
    assert response.status_code == 200
    payload = response.json()
    assert payload["definition_id"] == "general-mortality-rate"
    assert payload["drift_status"] in {"stable", "warning", "alert", "unknown"}
    assert payload["latest_observation_count"] >= 1

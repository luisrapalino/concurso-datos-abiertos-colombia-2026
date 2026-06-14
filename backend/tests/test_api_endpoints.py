import pytest


@pytest.mark.integration
def test_health_endpoint(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_predict_risk_endpoint(client) -> None:
    response = client.get(
        "/api/v1/predict-risk",
        params={"territorial_code": "05", "period": "2024-03"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["territorial_code"] == "05"
    assert payload["period"] == "2024-03"
    assert "score" in payload


@pytest.mark.integration
def test_anomalies_endpoint(client) -> None:
    response = client.get("/api/v1/anomalies")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert payload["total_items"] >= 1


@pytest.mark.integration
def test_territorial_trends_endpoint(client) -> None:
    response = client.get(
        "/api/v1/territorial-trends",
        params={"territorial_code": "05001", "horizon_weeks": 2},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["territorial_code"] == "05001"
    assert len(payload["points"]) >= 2


@pytest.mark.integration
def test_insights_endpoint(client) -> None:
    response = client.get("/api/v1/insights", params={"territorial_code": "05", "limit": 2})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2


@pytest.mark.integration
def test_validation_error_returns_consistent_payload(client) -> None:
    response = client.get(
        "/api/v1/predict-risk",
        params={"territorial_code": "invalid", "period": "2024-03"},
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "validation_error"
    assert payload["details"]

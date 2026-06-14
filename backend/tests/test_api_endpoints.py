import pytest


@pytest.mark.integration
def test_health_endpoint(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_health_indicators_endpoint(client) -> None:
    response = client.get(
        "/api/v1/health-indicators",
        params={"territorial_code": "05001", "period": "2020-01", "limit": 5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    observation = payload[0]
    assert observation["definition_id"] == "general-mortality-rate"
    assert observation["territorial_code"] == "05001"
    assert observation["period"] == "2020-01"
    assert "value" in observation
    assert observation["source_id"] == "datos-gov-mortality-indicators"


@pytest.mark.integration
def test_predict_risk_endpoint(client) -> None:
    response = client.get(
        "/api/v1/predict-risk",
        params={"territorial_code": "05001", "period": "2020-01"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["territorial_code"] == "05001"
    assert payload["period"] == "2020-01"
    assert payload["model_version"] == "mortality-relative-v1.0.0"
    assert "score" in payload
    assert payload["observed_value"] > 0
    assert payload["baseline_value"] > 0
    assert payload["drivers"]
    assert payload["feature_contributions"]
    assert payload["persisted"] is True


@pytest.mark.integration
def test_data_freshness_endpoint(client) -> None:
    response = client.get("/api/v1/data-freshness")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source_id"] == "datos-gov-mortality-indicators"
    assert payload["last_successful_ingestion_at"] is not None


@pytest.mark.integration
def test_territorial_risk_map_endpoint(client) -> None:
    response = client.get(
        "/api/v1/territorial-risk-map",
        params={"period": "2020-01", "limit": 5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    assert "latitude" in payload[0]
    assert "longitude" in payload[0]


@pytest.mark.integration
def test_predict_risk_returns_not_found_without_data(client) -> None:
    response = client.get(
        "/api/v1/predict-risk",
        params={"territorial_code": "05001", "period": "2099-01"},
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["code"] == "not_found"


@pytest.mark.integration
def test_anomalies_endpoint(client) -> None:
    response = client.get("/api/v1/anomalies", params={"page_size": 5})
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert payload["total_items"] >= 1
    assert payload["items"][0]["indicator_id"] == "general-mortality-rate"


@pytest.mark.integration
def test_territorial_trends_endpoint(client) -> None:
    response = client.get(
        "/api/v1/territorial-trends",
        params={"territorial_code": "05001", "horizon_weeks": 2},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["territorial_code"] == "05001"
    assert payload["model_version"] in {
        "linear-extrapolation-v1.0.0",
        "prophet-annual-v1.0.0",
    }
    assert payload["assumptions"]
    assert len(payload["points"]) >= 2
    assert any(point["kind"] == "historical" for point in payload["points"])
    assert any(point["kind"] == "forecast" for point in payload["points"])


@pytest.mark.integration
def test_data_quality_endpoint(client) -> None:
    response = client.get("/api/v1/data-quality")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_observations"] >= 1
    assert payload["distinct_territories"] >= 1
    assert "temporal_coverage_note" in payload


@pytest.mark.integration
def test_metrics_endpoint(client) -> None:
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "epintel_http_requests_total" in response.text


@pytest.mark.integration
def test_insights_endpoint(client) -> None:
    response = client.get(
        "/api/v1/insights",
        params={"territorial_code": "05001", "limit": 3},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    assert payload[0]["data_version"] == "composite-narrative-v1.0.0"
    assert payload[0]["sources"]
    assert payload[0]["system_context"]


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

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from config.settings import get_settings


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
def test_list_datasets_endpoint(client) -> None:
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    dataset = next(item for item in payload if item["definition_id"] == "general-mortality-rate")
    assert dataset["source_id"] == "datos-gov-mortality-indicators"
    assert dataset["records_ingested"] >= 0
    assert dataset["portal_url"].startswith("https://www.datos.gov.co/")
    assert dataset["api_url"].startswith("https://www.datos.gov.co/resource/")


@pytest.mark.integration
def test_list_municipal_datasets_endpoint(client) -> None:
    response = client.get("/api/v1/municipal-datasets")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 4
    pm25_rows = [row for row in payload if row["definition_id"] == "pm25-annual-mean"]
    assert len(pm25_rows) == 4
    assert pm25_rows[0]["active_binding_id"] == "pm25-annual-municipal"


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
    assert payload["total_items"] >= 0
    if payload["items"]:
        assert payload["items"][0]["indicator_id"] == "dengue-weekly-cases"


@pytest.mark.integration
def test_outbreak_prediction_endpoint(client) -> None:
    response = client.get(
        "/api/v1/outbreak-predictions",
        params={"territorial_code": "05001", "period": "2020-W01"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["territorial_code"] == "05001"
    assert payload["period"] == "2020-W01"
    assert payload["event_code"] == "210"
    assert payload["event_name"] == "DENGUE"
    assert payload["model_version"] == "outbreak-multivariate-v1.0.0"
    assert payload["outbreak_probability"] >= 0
    assert payload["feature_contributions"]
    assert payload["persisted"] is True


@pytest.mark.integration
def test_outbreak_map_endpoint(client) -> None:
    response = client.get(
        "/api/v1/outbreak-map",
        params={"period": "2020-W01", "limit": 5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    if payload:
        assert "latitude" in payload[0]
        assert "outbreak_probability" in payload[0]


@pytest.mark.integration
def test_outbreak_alerts_endpoint(client) -> None:
    response = client.get(
        "/api/v1/outbreak-alerts",
        params={"period": "2020-W01", "limit": 5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    if len(payload) >= 2:
        assert payload[0]["outbreak_probability"] >= payload[1]["outbreak_probability"]
    if payload:
        assert "baseline_cases" in payload[0]
        assert "municipality_name" in payload[0]


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
    assert payload["territorial_catalog"]["source_id"] == "dane-divipola"
    assert payload["territorial_catalog"]["municipality_count"] >= 1000


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
def test_data_drift_endpoint(client) -> None:
    response = client.get("/api/v1/data-drift")
    assert response.status_code == 200
    payload = response.json()
    assert payload["drift_status"] in {"stable", "warning", "alert", "unknown"}


@pytest.mark.integration
def test_territorial_report_endpoint(client) -> None:
    response = client.get(
        "/api/v1/territorial-report",
        params={"territorial_code": "05001", "period": "2020-01", "insight_limit": 2},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["territorial_code"] == "05001"
    assert payload["risk"]["score"] >= 0
    assert len(payload["insights"]) >= 1
    assert payload["drift_status"]


@pytest.mark.integration
def test_bias_analysis_endpoint(client) -> None:
    response = client.get(
        "/api/v1/bias-analysis",
        params={"period": "2020-01"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["national_mean"] >= 0
    assert len(payload["departments"]) >= 1


@pytest.mark.integration
def test_list_featured_municipalities_endpoint(client) -> None:
    response = client.get("/api/v1/municipalities/featured")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 4
    codes = {item["territorial_code"] for item in payload}
    assert codes == {"05001", "11001", "08001", "76001"}


@pytest.mark.integration
def test_search_municipalities_endpoint(client) -> None:
    response = client.get("/api/v1/municipalities", params={"search": "medell"})
    assert response.status_code == 200
    payload = response.json()
    assert any(item["territorial_code"] == "05001" for item in payload)


@pytest.mark.integration
def test_get_municipality_by_code_endpoint(client) -> None:
    response = client.get("/api/v1/municipalities/05001")
    assert response.status_code == 200
    payload = response.json()
    assert payload["territorial_code"] == "05001"
    assert payload["name"]


@pytest.mark.integration
def test_api_key_middleware_when_configured(client, monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", "test-secret-key")
    get_settings.cache_clear()
    protected = TestClient(create_app())
    try:
        denied = protected.get(
            "/api/v1/health-indicators",
            params={"territorial_code": "05001", "period": "2020-01", "limit": 1},
        )
        assert denied.status_code == 401

        allowed = protected.get(
            "/api/v1/health-indicators",
            params={"territorial_code": "05001", "period": "2020-01", "limit": 1},
            headers={"X-API-Key": "test-secret-key"},
        )
        assert allowed.status_code == 200

        health = protected.get("/health")
        assert health.status_code == 200
    finally:
        protected.close()
        monkeypatch.delenv("API_KEY", raising=False)
        get_settings.cache_clear()


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

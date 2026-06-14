from modules.anomaly_detection.application.dto import ListAnomaliesQueryDto
from modules.anomaly_detection.application.list_anomalies import ListAnomaliesUseCase
from modules.insights_generation.application.dto import ListInsightsQueryDto
from modules.insights_generation.application.generate_insights import GenerateInsightsUseCase
from modules.prediction_engine.application.dto import TerritorialTrendsQueryDto
from modules.prediction_engine.application.get_territorial_trends import GetTerritorialTrendsUseCase
from modules.territorial_risk.application.dto import PredictRiskQueryDto
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase


def test_predict_risk_use_case_returns_bounded_score() -> None:
    result = PredictRiskUseCase().execute(
        PredictRiskQueryDto(territorial_code="05", period="2024-03"),
    )
    assert 0 <= result.score <= 100
    assert result.model_version.startswith("stub-")


def test_list_anomalies_use_case_filters_by_territory() -> None:
    all_alerts = ListAnomaliesUseCase().execute(ListAnomaliesQueryDto())
    filtered = ListAnomaliesUseCase().execute(
        ListAnomaliesQueryDto(territorial_code="05"),
    )
    assert len(filtered.items) <= len(all_alerts.items)
    assert all(alert.territorial_code == "05" for alert in filtered.items)


def test_territorial_trends_use_case_returns_historical_and_forecast() -> None:
    result = GetTerritorialTrendsUseCase().execute(
        TerritorialTrendsQueryDto(territorial_code="05001", horizon_weeks=3),
    )
    kinds = {point.kind for point in result.points}
    assert "historical" in kinds
    assert "forecast" in kinds
    assert len([point for point in result.points if point.kind == "forecast"]) == 3


def test_generate_insights_use_case_respects_limit() -> None:
    insights = GenerateInsightsUseCase().execute(
        ListInsightsQueryDto(territorial_code="05", limit=1),
    )
    assert len(insights) == 1

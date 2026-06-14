from datetime import UTC, datetime

from modules.anomaly_detection.domain.detection import AnomalyAlert, AnomalySeverity
from modules.insights_generation.domain.narrative import (
    INSIGHTS_VERSION,
    TerritorialInsightContext,
    TrendSummary,
    generate_insights,
)
from modules.territorial_risk.domain.risk_score import RiskClassification, RiskScore


def test_generate_insights_includes_risk_anomaly_and_coverage() -> None:
    context = TerritorialInsightContext(
        territorial_code="05001",
        indicator_name="Tasa de mortalidad general",
        risk_score=RiskScore(
            territorial_code="05001",
            period="2020-01",
            score=75.0,
            classification=RiskClassification.HIGH,
            model_version="mortality-relative-v1.0.0",
            observed_value=12.0,
            baseline_value=8.0,
            indicator_definition_id="general-mortality-rate",
            assumptions=(),
            drivers=(),
            feature_contributions=(),
            generated_at=datetime.now(tz=UTC),
        ),
        anomaly=AnomalyAlert(
            id="anomaly:general-mortality-rate:05001:2020-01",
            territorial_code="05001",
            indicator_id="general-mortality-rate",
            indicator_name="Tasa de mortalidad general",
            detected_on=datetime(2020, 1, 1).date(),
            severity=AnomalySeverity.HIGH,
            description="Test anomaly.",
            baseline_value=8.0,
            observed_value=12.0,
        ),
        trend=TrendSummary(
            latest_period="2020-01",
            latest_value=12.0,
            previous_value=10.0,
            forecast_next_value=14.0,
            historical_points=3,
        ),
        generated_at=datetime.now(tz=UTC),
    )

    insights = generate_insights(context)
    assert len(insights) >= 4
    assert insights[0].data_version == INSIGHTS_VERSION
    assert any("riesgo" in insight.title.lower() for insight in insights)

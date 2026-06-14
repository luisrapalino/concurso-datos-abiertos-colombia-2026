from datetime import UTC, datetime

from modules.anomaly_detection.domain.detection import evaluate_observation
from modules.anomaly_detection.domain.repositories import CuratedObservationsReader
from modules.insights_generation.application.dto import (
    InsightConfidence,
    InsightReadDto,
    ListInsightsQueryDto,
)
from modules.insights_generation.domain.narrative import (
    INSIGHTS_VERSION,
    Insight,
    TerritorialInsightContext,
    TrendSummary,
    generate_insights,
)
from modules.prediction_engine.domain.forecast import linear_extrapolation_forecast
from modules.territorial_risk.domain.repositories import TerritorialRiskDataPort
from modules.territorial_risk.domain.risk_score import GENERAL_MORTALITY_DEFINITION_ID
from modules.territorial_risk.domain.scoring import compute_relative_mortality_score


class GenerateInsightsUseCase:
    """Builds narrative insights from risk, anomalies and territorial trends."""

    def __init__(
        self,
        reader: CuratedObservationsReader,
        risk_data: TerritorialRiskDataPort,
    ) -> None:
        self._reader = reader
        self._risk_data = risk_data

    def execute(self, query: ListInsightsQueryDto) -> list[InsightReadDto]:
        territorial_code = str(query.territorial_code)
        indicator_name, series = self._reader.list_territorial_series(
            territorial_code,
            GENERAL_MORTALITY_DEFINITION_ID,
        )
        if not series:
            return []

        latest = series[-1]
        previous = series[-2] if len(series) >= 2 else None
        forecast = linear_extrapolation_forecast(series, steps=1)
        forecast_value = forecast[0].value if forecast else None

        observation = self._risk_data.get_mortality_observation(territorial_code, latest.period)
        national_median = self._risk_data.get_national_median_mortality(latest.period)
        risk_score = None
        if observation is not None and national_median is not None:
            risk_score = compute_relative_mortality_score(
                observation,
                national_median=national_median,
                generated_at=datetime.now(tz=UTC),
            )

        anomaly = None
        for item in self._reader.list_observations_with_period_median(
            GENERAL_MORTALITY_DEFINITION_ID,
            territorial_code=territorial_code,
        ):
            if item.period == latest.period:
                anomaly = evaluate_observation(item)
                break

        context = TerritorialInsightContext(
            territorial_code=territorial_code,
            indicator_name=indicator_name,
            risk_score=risk_score,
            anomaly=anomaly,
            trend=TrendSummary(
                latest_period=latest.period,
                latest_value=float(latest.value),
                previous_value=float(previous.value) if previous else None,
                forecast_next_value=forecast_value,
                historical_points=len(series),
            ),
            generated_at=datetime.now(tz=UTC),
        )

        insights = generate_insights(context)
        system_context = _build_system_context(context)
        return [
            _to_dto(insight, analysis_period=latest.period, system_context=system_context)
            for insight in insights[: query.limit]
        ]


def _build_system_context(context: TerritorialInsightContext) -> str:
    risk_version = context.risk_score.model_version if context.risk_score else "n/a"
    return (
        f"Sistema: ventana de {context.trend.historical_points} periodo(s), "
        f"último {context.trend.latest_period}. "
        f"Modelo de riesgo {risk_version}; narrativa {INSIGHTS_VERSION}. "
        "No sustituye validación epidemiológica."
    )


def _to_dto(
    insight: Insight,
    *,
    analysis_period: str,
    system_context: str,
) -> InsightReadDto:
    return InsightReadDto(
        id=insight.id,
        territorial_code=insight.territorial_code,
        title=insight.title,
        narrative=insight.narrative,
        confidence=InsightConfidence(insight.confidence.value),
        data_version=insight.data_version or INSIGHTS_VERSION,
        sources=list(insight.sources),
        analysis_period=analysis_period,
        system_context=system_context,
    )

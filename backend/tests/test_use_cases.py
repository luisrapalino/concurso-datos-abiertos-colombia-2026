from decimal import Decimal

from modules.anomaly_detection.application.dto import ListAnomaliesQueryDto
from modules.anomaly_detection.application.list_anomalies import ListAnomaliesUseCase
from modules.anomaly_detection.domain.detection import ObservationWithBaseline
from modules.anomaly_detection.domain.repositories import (
    TerritorialSeriesPoint,
)
from modules.prediction_engine.application.dto import TerritorialTrendsQueryDto
from modules.prediction_engine.application.get_territorial_trends import GetTerritorialTrendsUseCase


class FakeCuratedObservationsReader:
    def list_observations_with_period_median(
        self,
        definition_id: str,
        *,
        territorial_code: str | None = None,
    ) -> list[ObservationWithBaseline]:
        observations = [
            ObservationWithBaseline(
                territorial_code="05001",
                period="2020-01",
                value=Decimal("12.0"),
                baseline=Decimal("8.0"),
                definition_id=definition_id,
                definition_name="Tasa de mortalidad general",
            ),
            ObservationWithBaseline(
                territorial_code="05002",
                period="2020-01",
                value=Decimal("7.0"),
                baseline=Decimal("8.0"),
                definition_id=definition_id,
                definition_name="Tasa de mortalidad general",
            ),
        ]
        if territorial_code is None:
            return observations
        return [item for item in observations if item.territorial_code == territorial_code]

    def list_territorial_series(
        self,
        territorial_code: str,
        definition_id: str,
    ) -> tuple[str, list[TerritorialSeriesPoint]]:
        del definition_id
        return "Tasa de mortalidad general", [
            TerritorialSeriesPoint(period="2018-01", value=Decimal("6.0")),
            TerritorialSeriesPoint(period="2019-01", value=Decimal("7.0")),
            TerritorialSeriesPoint(period="2020-01", value=Decimal("8.0")),
        ]


def test_list_anomalies_use_case_filters_by_territory() -> None:
    reader = FakeCuratedObservationsReader()
    all_alerts = ListAnomaliesUseCase(reader).execute(ListAnomaliesQueryDto())
    filtered = ListAnomaliesUseCase(reader).execute(
        ListAnomaliesQueryDto(territorial_code="05001"),
    )
    assert len(filtered.items) <= len(all_alerts.items)
    assert all(alert.territorial_code == "05001" for alert in filtered.items)
    assert filtered.items[0].indicator_id == "general-mortality-rate"


def test_territorial_trends_use_case_returns_historical_and_forecast() -> None:
    result = GetTerritorialTrendsUseCase(FakeCuratedObservationsReader()).execute(
        TerritorialTrendsQueryDto(territorial_code="05001", horizon_weeks=3),
    )
    kinds = {point.kind for point in result.points}
    assert "historical" in kinds
    assert "forecast" in kinds
    assert len([point for point in result.points if point.kind == "forecast"]) == 3
    assert result.model_version == "linear-extrapolation-v1.0.0"
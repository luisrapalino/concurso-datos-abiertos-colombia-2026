from modules.anomaly_detection.domain.repositories import CuratedObservationsReader
from modules.prediction_engine.application.dto import (
    TerritorialTrendReadDto,
    TerritorialTrendsQueryDto,
    TrendPointDto,
    TrendPointKind,
)
from modules.prediction_engine.domain.forecast import ForecastServicePort
from shared.exceptions import EntityNotFoundError
from shared.period import Period


class GetTerritorialTrendsUseCase:
    """Returns historical series from curated data with a versioned forecast."""

    def __init__(
        self,
        reader: CuratedObservationsReader,
        forecast_service: ForecastServicePort,
    ) -> None:
        self._reader = reader
        self._forecast_service = forecast_service

    def execute(self, query: TerritorialTrendsQueryDto) -> TerritorialTrendReadDto:
        definition_id = query.indicator_id
        indicator_name, historical = self._reader.list_territorial_series(
            str(query.territorial_code),
            definition_id,
        )
        if not historical:
            raise EntityNotFoundError(
                "territorial_series",
                f"{query.territorial_code}@{definition_id}",
            )

        historical_points = [
            TrendPointDto(
                period=Period(point.period),
                value=round(float(point.value), 4),
                kind=TrendPointKind.HISTORICAL,
            )
            for point in historical
        ]
        forecast = self._forecast_service.forecast(
            historical,
            steps=query.horizon_weeks,
        )
        forecast_points = [
            TrendPointDto(
                period=Period(point.period),
                value=point.value,
                kind=TrendPointKind.FORECAST,
            )
            for point in forecast.points
        ]

        return TerritorialTrendReadDto(
            territorial_code=query.territorial_code,
            indicator_id=definition_id,
            indicator_name=indicator_name,
            points=[*historical_points, *forecast_points],
            forecast_horizon_weeks=query.horizon_weeks,
            model_version=forecast.model_version,
            assumptions=list(forecast.assumptions),
        )

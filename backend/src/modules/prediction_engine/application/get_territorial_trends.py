from modules.anomaly_detection.domain.repositories import CuratedObservationsReader
from modules.prediction_engine.application.dto import (
    TerritorialTrendReadDto,
    TerritorialTrendsQueryDto,
    TrendPointDto,
    TrendPointKind,
)
from modules.prediction_engine.domain.forecast import (
    FORECAST_VERSION,
    linear_extrapolation_forecast,
)
from shared.exceptions import EntityNotFoundError
from shared.period import Period


class GetTerritorialTrendsUseCase:
    """Returns historical series from curated data with simple linear forecast."""

    def __init__(self, reader: CuratedObservationsReader) -> None:
        self._reader = reader

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
        forecast_points = [
            TrendPointDto(
                period=Period(point.period),
                value=point.value,
                kind=TrendPointKind.FORECAST,
            )
            for point in linear_extrapolation_forecast(
                historical,
                steps=query.horizon_weeks,
            )
        ]

        return TerritorialTrendReadDto(
            territorial_code=query.territorial_code,
            indicator_id=definition_id,
            indicator_name=indicator_name,
            points=[*historical_points, *forecast_points],
            forecast_horizon_weeks=query.horizon_weeks,
            model_version=FORECAST_VERSION,
        )

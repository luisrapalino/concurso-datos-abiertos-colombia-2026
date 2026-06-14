from modules.prediction_engine.application.dto import (
    TerritorialTrendReadDto,
    TerritorialTrendsQueryDto,
    TrendPointDto,
    TrendPointKind,
)
from shared.period import Period


class GetTerritorialTrendsUseCase:
    """Returns stub historical and forecast points until Prophet pipelines exist."""

    _INDICATOR_NAMES = {
        "stub-mortality-rate": "Crude mortality rate (placeholder)",
    }

    def execute(self, query: TerritorialTrendsQueryDto) -> TerritorialTrendReadDto:
        historical = self._historical_points(query.territorial_code, query.indicator_id)
        forecast = self._forecast_points(
            query.territorial_code,
            query.indicator_id,
            query.horizon_weeks,
            start_value=historical[-1].value,
        )
        return TerritorialTrendReadDto(
            territorial_code=query.territorial_code,
            indicator_id=query.indicator_id,
            indicator_name=self._INDICATOR_NAMES.get(query.indicator_id, query.indicator_id),
            points=[*historical, *forecast],
            forecast_horizon_weeks=query.horizon_weeks,
            model_version="stub-prophet-v0.1.0",
        )

    @staticmethod
    def _historical_points(territorial_code: str, indicator_id: str) -> list[TrendPointDto]:
        seed = sum(ord(char) for char in territorial_code) + len(indicator_id)
        periods = ("2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06")
        return [
            TrendPointDto(
                period=Period(period),
                value=round(10 + ((seed + index * 3) % 15) + index * 0.4, 2),
                kind=TrendPointKind.HISTORICAL,
            )
            for index, period in enumerate(periods)
        ]

    @staticmethod
    def _forecast_points(
        territorial_code: str,
        indicator_id: str,
        horizon_weeks: int,
        *,
        start_value: float,
    ) -> list[TrendPointDto]:
        seed = sum(ord(char) for char in territorial_code) + len(indicator_id)
        periods = ("2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12")
        return [
            TrendPointDto(
                period=Period(periods[index]),
                value=round(start_value + ((seed + index) % 5) * 0.6, 2),
                kind=TrendPointKind.FORECAST,
            )
            for index in range(min(horizon_weeks, len(periods)))
        ]

from modules.anomaly_detection.domain.repositories import TerritorialSeriesPoint
from modules.prediction_engine.domain.forecast import (
    LINEAR_FORECAST_VERSION,
    MIN_PROPHET_POINTS,
    PROPHET_FORECAST_VERSION,
    ForecastPoint,
    ForecastResult,
    ForecastServicePort,
    linear_extrapolation_forecast,
)


class CompositeForecastService(ForecastServicePort):
    """Uses Prophet for annual series when available; falls back to linear extrapolation."""

    def forecast(
        self,
        historical: list[TerritorialSeriesPoint],
        *,
        steps: int,
    ) -> ForecastResult:
        if len(historical) >= MIN_PROPHET_POINTS:
            prophet_result = _try_prophet_forecast(historical, steps=steps)
            if prophet_result is not None:
                return prophet_result

        linear_points = linear_extrapolation_forecast(historical, steps=steps)
        return ForecastResult(
            points=tuple(linear_points),
            model_version=LINEAR_FORECAST_VERSION,
            assumptions=(
                "Forecast uses the slope between the last two annual observations.",
                "Annual indicators use period convention YYYY-01.",
                "Short horizons only; not validated for operational planning.",
            ),
        )


class LinearForecastService(ForecastServicePort):
    """Deterministic linear extrapolation for tests and fallback."""

    def forecast(
        self,
        historical: list[TerritorialSeriesPoint],
        *,
        steps: int,
    ) -> ForecastResult:
        linear_points = linear_extrapolation_forecast(historical, steps=steps)
        return ForecastResult(
            points=tuple(linear_points),
            model_version=LINEAR_FORECAST_VERSION,
            assumptions=("Linear extrapolation fallback.",),
        )


def _try_prophet_forecast(
    historical: list[TerritorialSeriesPoint],
    *,
    steps: int,
) -> ForecastResult | None:
    try:
        import pandas as pd
        from prophet import Prophet
    except ImportError:
        return None

    sorted_points = sorted(historical, key=lambda point: point.period)
    frame = pd.DataFrame(
        {
            "ds": [f"{point.period[:4]}-07-01" for point in sorted_points],
            "y": [float(point.value) for point in sorted_points],
        },
    )
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    model.fit(frame)
    future = model.make_future_dataframe(periods=steps, freq="YS")
    forecast_frame = model.predict(future).tail(steps)

    points: list[ForecastPoint] = []
    last_year = int(sorted_points[-1].period[:4])
    for index, row in enumerate(forecast_frame.itertuples(), start=1):
        year = last_year + index
        points.append(
            ForecastPoint(
                period=f"{year:04d}-01",
                value=round(float(row.yhat), 4),
            ),
        )

    return ForecastResult(
        points=tuple(points),
        model_version=PROPHET_FORECAST_VERSION,
        assumptions=(
            "Forecast generated with Facebook Prophet on annual mortality observations.",
            "Uncertainty intervals are not exposed in the MVP API.",
            "Correlation in historical data does not imply causal projections.",
        ),
    )

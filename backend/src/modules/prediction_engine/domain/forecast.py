from dataclasses import dataclass
from decimal import Decimal

from modules.anomaly_detection.domain.repositories import TerritorialSeriesPoint

FORECAST_VERSION = "linear-extrapolation-v1.0.0"


@dataclass(frozen=True, slots=True)
class ForecastPoint:
    period: str
    value: float


def next_annual_period(period: str) -> str:
    year = int(period[:4]) + 1
    return f"{year:04d}-01"


def linear_extrapolation_forecast(
    historical: list[TerritorialSeriesPoint],
    *,
    steps: int,
) -> list[ForecastPoint]:
    if not historical:
        return []

    sorted_points = sorted(historical, key=lambda point: point.period)
    last = sorted_points[-1]
    if len(sorted_points) == 1:
        slope = Decimal("0")
    else:
        previous = sorted_points[-2]
        slope = last.value - previous.value

    forecasts: list[ForecastPoint] = []
    current_period = last.period
    current_value = last.value
    for _ in range(steps):
        current_period = next_annual_period(current_period)
        current_value = current_value + slope
        forecasts.append(
            ForecastPoint(period=current_period, value=round(float(current_value), 4)),
        )
    return forecasts

from decimal import Decimal

from modules.anomaly_detection.domain.detection import (
    ObservationWithBaseline,
    evaluate_observation,
)
from modules.anomaly_detection.domain.repositories import TerritorialSeriesPoint
from modules.prediction_engine.domain.forecast import linear_extrapolation_forecast


def test_evaluate_observation_flags_high_ratio() -> None:
    observation = ObservationWithBaseline(
        territorial_code="05001",
        period="2020-01",
        value=Decimal("20.0"),
        baseline=Decimal("8.0"),
        definition_id="general-mortality-rate",
        definition_name="Tasa de mortalidad general",
    )
    alert = evaluate_observation(observation)
    assert alert is not None
    assert alert.severity == "high"


def test_evaluate_observation_ignores_normal_values() -> None:
    observation = ObservationWithBaseline(
        territorial_code="05001",
        period="2020-01",
        value=Decimal("8.5"),
        baseline=Decimal("8.0"),
        definition_id="general-mortality-rate",
        definition_name="Tasa de mortalidad general",
    )
    assert evaluate_observation(observation) is None


def test_linear_extrapolation_forecast_projects_next_periods() -> None:
    historical = [
        TerritorialSeriesPoint(period="2018-01", value=Decimal("6.0")),
        TerritorialSeriesPoint(period="2019-01", value=Decimal("7.0")),
        TerritorialSeriesPoint(period="2020-01", value=Decimal("8.0")),
    ]
    forecast = linear_extrapolation_forecast(historical, steps=2)
    assert len(forecast) == 2
    assert forecast[0].period == "2021-01"
    assert forecast[0].value == 9.0

from decimal import Decimal

import pytest

from modules.territorial_risk.application.dto import PredictRiskQueryDto
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase
from modules.territorial_risk.domain.risk_score import MortalityObservation
from shared.exceptions import EntityNotFoundError


class FakeTerritorialRiskDataPort:
    def __init__(self) -> None:
        self.observation = MortalityObservation(
            definition_id="general-mortality-rate",
            territorial_code="05001",
            period="2020-01",
            value=Decimal("10.0"),
        )
        self.median = Decimal("8.0")

    def get_mortality_observation(
        self,
        territorial_code: str,
        period: str,
    ) -> MortalityObservation | None:
        if (
            territorial_code == self.observation.territorial_code
            and period == self.observation.period
        ):
            return self.observation
        return None

    def get_national_median_mortality(self, period: str) -> Decimal | None:
        if period == self.observation.period:
            return self.median
        return None


def test_predict_risk_use_case_returns_bounded_score() -> None:
    result = PredictRiskUseCase(FakeTerritorialRiskDataPort()).execute(
        PredictRiskQueryDto(territorial_code="05001", period="2020-01"),
    )
    assert 0 <= result.score <= 100
    assert result.model_version == "mortality-relative-v1.0.0"
    assert result.observed_value == 10.0
    assert result.baseline_value == 8.0
    assert len(result.drivers) >= 1


def test_predict_risk_use_case_raises_when_observation_missing() -> None:
    use_case = PredictRiskUseCase(FakeTerritorialRiskDataPort())
    with pytest.raises(EntityNotFoundError):
        use_case.execute(PredictRiskQueryDto(territorial_code="99999", period="2020-01"))

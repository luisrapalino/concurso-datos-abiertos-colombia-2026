from decimal import Decimal

import pytest

from modules.territorial_risk.application.dto import PredictRiskQueryDto
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase
from modules.territorial_risk.domain.risk_score import MortalityObservation, RiskScore
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

    def list_territorial_codes_for_period(
        self,
        period: str,
        *,
        definition_id: str = "general-mortality-rate",
        limit: int = 500,
    ) -> list[str]:
        del definition_id, limit
        if period == self.observation.period:
            return [self.observation.territorial_code]
        return []


class InMemoryRiskScoreRepository:
    def __init__(self) -> None:
        self.saved: list[RiskScore] = []

    def get(
        self,
        *,
        territorial_code: str,
        period: str,
        definition_id: str,
        model_version: str,
    ) -> RiskScore | None:
        del definition_id
        for item in self.saved:
            if (
                item.territorial_code == territorial_code
                and item.period == period
                and item.model_version == model_version
            ):
                return item
        return None

    def save(self, risk_score: RiskScore) -> None:
        self.saved = [item for item in self.saved if item.period != risk_score.period]
        self.saved.append(risk_score)

    def list_for_period(
        self,
        *,
        period: str,
        definition_id: str,
        model_version: str,
        limit: int = 500,
    ) -> list[RiskScore]:
        del definition_id, model_version, limit
        return [item for item in self.saved if item.period == period]


def test_predict_risk_use_case_returns_bounded_score() -> None:
    repository = InMemoryRiskScoreRepository()
    result = PredictRiskUseCase(FakeTerritorialRiskDataPort(), repository).execute(
        PredictRiskQueryDto(territorial_code="05001", period="2020-01"),
    )
    assert 0 <= result.score <= 100
    assert result.model_version == "mortality-relative-v1.0.0"
    assert result.observed_value == 10.0
    assert result.baseline_value == 8.0
    assert len(result.drivers) >= 1
    assert len(result.feature_contributions) == 3
    assert result.persisted is True
    assert len(repository.saved) == 1


def test_predict_risk_use_case_reads_persisted_score() -> None:
    repository = InMemoryRiskScoreRepository()
    use_case = PredictRiskUseCase(FakeTerritorialRiskDataPort(), repository)
    first = use_case.execute(PredictRiskQueryDto(territorial_code="05001", period="2020-01"))
    second = use_case.execute(PredictRiskQueryDto(territorial_code="05001", period="2020-01"))
    assert first.score == second.score
    assert len(repository.saved) == 1


def test_predict_risk_use_case_raises_when_observation_missing() -> None:
    use_case = PredictRiskUseCase(
        FakeTerritorialRiskDataPort(),
        InMemoryRiskScoreRepository(),
    )
    with pytest.raises(EntityNotFoundError):
        use_case.execute(PredictRiskQueryDto(territorial_code="99999", period="2020-01"))

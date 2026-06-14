from datetime import UTC, datetime

from modules.territorial_risk.application.dto import (
    PredictRiskQueryDto,
    RiskClassification,
    RiskScoreReadDto,
)
from shared.period import Period
from shared.territorial import TerritorialCode


class PredictRiskUseCase:
    """Returns a stub territorial risk score until real scoring is implemented."""

    _STUB_ASSUMPTIONS = (
        "Placeholder scoring based on synthetic baseline data.",
        "Not validated for operational public health decisions.",
        "Territorial coverage may be partial during MVP rollout.",
    )

    def execute(self, query: PredictRiskQueryDto) -> RiskScoreReadDto:
        score = self._stub_score(query.territorial_code, query.period)
        return RiskScoreReadDto(
            territorial_code=query.territorial_code,
            period=query.period,
            score=score,
            classification=self._classify(score),
            model_version="stub-rules-v0.1.0",
            assumptions=list(self._STUB_ASSUMPTIONS),
            generated_at=datetime.now(tz=UTC),
        )

    @staticmethod
    def _stub_score(territorial_code: TerritorialCode, period: Period) -> float:
        seed = sum(ord(char) for char in territorial_code) + period.year + period.month
        return round((seed * 7) % 101, 2)

    @staticmethod
    def _classify(score: float) -> RiskClassification:
        if score >= 80:
            return RiskClassification.CRITICAL
        if score >= 60:
            return RiskClassification.HIGH
        if score >= 35:
            return RiskClassification.MEDIUM
        return RiskClassification.LOW

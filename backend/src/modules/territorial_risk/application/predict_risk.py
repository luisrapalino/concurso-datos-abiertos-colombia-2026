from datetime import UTC, datetime

from modules.territorial_risk.application.dto import PredictRiskQueryDto, RiskScoreReadDto
from modules.territorial_risk.domain.repositories import TerritorialRiskDataPort
from modules.territorial_risk.domain.risk_score import GENERAL_MORTALITY_DEFINITION_ID, RiskScore
from modules.territorial_risk.domain.scoring import compute_relative_mortality_score
from shared.exceptions import EntityNotFoundError


class PredictRiskUseCase:
    """Computes territorial risk from curated mortality indicators."""

    def __init__(self, data_port: TerritorialRiskDataPort) -> None:
        self._data_port = data_port

    def execute(self, query: PredictRiskQueryDto) -> RiskScoreReadDto:
        territorial_code = str(query.territorial_code)
        period = str(query.period)

        observation = self._data_port.get_mortality_observation(territorial_code, period)
        if observation is None:
            raise EntityNotFoundError(
                "mortality_observation",
                f"{territorial_code}@{period}",
            )

        national_median = self._data_port.get_national_median_mortality(period)
        if national_median is None:
            raise EntityNotFoundError("national_mortality_baseline", period)

        risk_score = compute_relative_mortality_score(
            observation,
            national_median=national_median,
            generated_at=datetime.now(tz=UTC),
        )
        return _to_dto(risk_score)


def _to_dto(risk_score: RiskScore) -> RiskScoreReadDto:
    return RiskScoreReadDto(
        territorial_code=risk_score.territorial_code,
        period=risk_score.period,
        score=risk_score.score,
        classification=risk_score.classification,
        model_version=risk_score.model_version,
        indicator_definition_id=(
            risk_score.indicator_definition_id or GENERAL_MORTALITY_DEFINITION_ID
        ),
        observed_value=risk_score.observed_value,
        baseline_value=risk_score.baseline_value,
        assumptions=list(risk_score.assumptions),
        drivers=list(risk_score.drivers),
        generated_at=risk_score.generated_at,
    )

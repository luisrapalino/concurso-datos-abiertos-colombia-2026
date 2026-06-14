from datetime import UTC, datetime

from modules.territorial_risk.application.dto import PredictRiskQueryDto, RiskScoreReadDto
from modules.territorial_risk.domain.repositories import (
    RiskScoreRepository,
    TerritorialRiskDataPort,
)
from modules.territorial_risk.domain.risk_score import GENERAL_MORTALITY_DEFINITION_ID, RiskScore
from modules.territorial_risk.domain.scoring import compute_relative_mortality_score
from shared.exceptions import EntityNotFoundError


class PredictRiskUseCase:
    """Computes territorial risk from curated mortality indicators."""

    def __init__(
        self,
        data_port: TerritorialRiskDataPort,
        risk_score_repository: RiskScoreRepository,
    ) -> None:
        self._data_port = data_port
        self._risk_score_repository = risk_score_repository

    def execute(self, query: PredictRiskQueryDto) -> RiskScoreReadDto:
        territorial_code = str(query.territorial_code)
        period = str(query.period)

        cached = self._risk_score_repository.get(
            territorial_code=territorial_code,
            period=period,
            definition_id=GENERAL_MORTALITY_DEFINITION_ID,
            model_version=_current_model_version(),
        )
        if cached is not None and cached.feature_contributions:
            return _to_dto(cached, persisted=True)

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
        self._risk_score_repository.save(risk_score)
        return _to_dto(risk_score, persisted=True)


def _current_model_version() -> str:
    from modules.territorial_risk.domain.risk_score import RULES_VERSION

    return RULES_VERSION


def _to_dto(risk_score: RiskScore, *, persisted: bool) -> RiskScoreReadDto:
    from modules.territorial_risk.application.dto import FeatureContributionReadDto

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
        feature_contributions=[
            FeatureContributionReadDto(
                feature=item.feature,
                value=item.value,
                contribution=item.contribution,
                description=item.description,
            )
            for item in risk_score.feature_contributions
        ],
        generated_at=risk_score.generated_at,
        persisted=persisted,
    )

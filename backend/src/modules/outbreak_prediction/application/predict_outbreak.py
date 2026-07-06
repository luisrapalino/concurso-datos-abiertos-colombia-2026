from datetime import UTC, datetime

from modules.outbreak_prediction.application.dto import (
    FeatureContributionDto,
    OutbreakPredictionReadDto,
    PredictOutbreakQueryDto,
)
from modules.outbreak_prediction.application.ports.promoted_outbreak_model_port import (
    PromotedOutbreakModelPort,
)
from modules.outbreak_prediction.domain.outbreak_prediction import (
    DENGUE_EVENT_CODE,
    DENGUE_EVENT_NAME,
    OUTBREAK_RULES_VERSION,
    OutbreakFeatureSnapshot,
    OutbreakPrediction,
)
from modules.outbreak_prediction.domain.repositories import (
    OutbreakDataPort,
    OutbreakPredictionRepository,
)
from modules.outbreak_prediction.domain.scoring import compute_outbreak_prediction
from modules.outbreak_prediction.infrastructure.ml.file_promoted_outbreak_model_adapter import (
    NullPromotedOutbreakModelAdapter,
)
from shared.exceptions import EntityNotFoundError


class PredictOutbreakUseCase:
    """Predicts transmissible disease outbreak probability from multivariate features."""

    def __init__(
        self,
        data_port: OutbreakDataPort,
        repository: OutbreakPredictionRepository,
        promoted_model: PromotedOutbreakModelPort | None = None,
    ) -> None:
        self._data_port = data_port
        self._repository = repository
        self._promoted_model = promoted_model or NullPromotedOutbreakModelAdapter()

    def execute(self, query: PredictOutbreakQueryDto) -> OutbreakPredictionReadDto:
        territorial_code = str(query.territorial_code)
        period = str(query.period)
        event_code = str(query.event_code)
        model_version = _current_model_version(self._promoted_model)

        cached = self._repository.get(
            territorial_code=territorial_code,
            period=period,
            event_code=event_code,
            model_version=model_version,
        )
        if cached is not None and cached.feature_contributions:
            return _to_dto(cached, persisted=True)

        bundle = self._data_port.get_feature_bundle(
            territorial_code,
            period,
            event_code=event_code,
        )
        if bundle is None:
            raise EntityNotFoundError(
                "outbreak_features",
                f"{territorial_code}@{period}@{event_code}",
            )

        prediction = compute_outbreak_prediction(
            OutbreakFeatureSnapshot(
                territorial_code=bundle.territorial_code,
                period=bundle.period,
                event_code=bundle.event_code,
                event_name=bundle.event_name,
                observed_cases=float(bundle.observed_cases),
                baseline_cases=float(bundle.baseline_cases),
                previous_week_cases=(
                    float(bundle.previous_week_cases)
                    if bundle.previous_week_cases is not None
                    else None
                ),
                vaccination_coverage_pct=(
                    float(bundle.vaccination_coverage_pct)
                    if bundle.vaccination_coverage_pct is not None
                    else None
                ),
                health_access_pct=(
                    float(bundle.health_access_pct)
                    if bundle.health_access_pct is not None
                    else None
                ),
                pm25_ug_m3=float(bundle.pm25_ug_m3) if bundle.pm25_ug_m3 is not None else None,
            ),
            generated_at=datetime.now(tz=UTC),
            promoted_model=self._promoted_model,
        )
        self._repository.save(prediction)
        return _to_dto(prediction, persisted=True)


def _current_model_version(promoted_model: PromotedOutbreakModelPort) -> str:
    active_version = promoted_model.active_model_version()
    return active_version or OUTBREAK_RULES_VERSION


def _to_dto(prediction: OutbreakPrediction, *, persisted: bool) -> OutbreakPredictionReadDto:
    return OutbreakPredictionReadDto(
        territorial_code=prediction.territorial_code,
        period=prediction.period,
        event_code=prediction.event_code or DENGUE_EVENT_CODE,
        event_name=prediction.event_name or DENGUE_EVENT_NAME,
        outbreak_probability=prediction.outbreak_probability,
        classification=prediction.classification,
        model_version=prediction.model_version,
        observed_cases=prediction.observed_cases,
        baseline_cases=prediction.baseline_cases,
        assumptions=list(prediction.assumptions),
        drivers=list(prediction.drivers),
        feature_contributions=[
            FeatureContributionDto(
                feature=item.feature,
                contribution=item.contribution,
                direction=item.direction,
            )
            for item in prediction.feature_contributions
        ],
        generated_at=prediction.generated_at,
        persisted=persisted,
    )

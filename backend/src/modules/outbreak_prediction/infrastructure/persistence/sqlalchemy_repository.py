from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from modules.outbreak_prediction.domain.outbreak_prediction import OutbreakPrediction
from modules.outbreak_prediction.domain.repositories import OutbreakPredictionRepository
from modules.outbreak_prediction.infrastructure.persistence.orm_models import OutbreakPredictionRow


class SqlAlchemyOutbreakPredictionRepository(OutbreakPredictionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(
        self,
        *,
        territorial_code: str,
        period: str,
        event_code: str,
        model_version: str,
    ) -> OutbreakPrediction | None:
        row = self._session.get(
            OutbreakPredictionRow,
            _prediction_id(territorial_code, period, event_code, model_version),
        )
        if row is None:
            return None
        return _to_domain(row)

    def save(self, prediction: OutbreakPrediction) -> None:
        row = {
            "id": _prediction_id(
                prediction.territorial_code,
                prediction.period,
                prediction.event_code,
                prediction.model_version,
            ),
            "territorial_code": prediction.territorial_code,
            "period": prediction.period,
            "event_code": prediction.event_code,
            "event_name": prediction.event_name,
            "outbreak_probability": prediction.outbreak_probability,
            "classification": prediction.classification.value,
            "model_version": prediction.model_version,
            "observed_cases": prediction.observed_cases,
            "baseline_cases": prediction.baseline_cases,
            "assumptions": list(prediction.assumptions),
            "drivers": list(prediction.drivers),
            "feature_contributions": [
                {
                    "feature": item.feature,
                    "contribution": item.contribution,
                    "direction": item.direction,
                }
                for item in prediction.feature_contributions
            ],
            "generated_at": prediction.generated_at,
        }
        stmt = insert(OutbreakPredictionRow).values(row)
        stmt = stmt.on_conflict_do_update(
            index_elements=["territorial_code", "period", "event_code", "model_version"],
            set_={
                "outbreak_probability": stmt.excluded.outbreak_probability,
                "classification": stmt.excluded.classification,
                "observed_cases": stmt.excluded.observed_cases,
                "baseline_cases": stmt.excluded.baseline_cases,
                "assumptions": stmt.excluded.assumptions,
                "drivers": stmt.excluded.drivers,
                "feature_contributions": stmt.excluded.feature_contributions,
                "generated_at": stmt.excluded.generated_at,
            },
        )
        self._session.execute(stmt)
        self._session.commit()


def _prediction_id(
    territorial_code: str,
    period: str,
    event_code: str,
    model_version: str,
) -> str:
    return f"{event_code}:{territorial_code}:{period}:{model_version}"


def _to_domain(row: OutbreakPredictionRow) -> OutbreakPrediction:
    from modules.outbreak_prediction.domain.outbreak_prediction import (
        FeatureContribution,
        OutbreakClassification,
    )

    return OutbreakPrediction(
        territorial_code=row.territorial_code,
        period=row.period,
        event_code=row.event_code,
        event_name=row.event_name,
        outbreak_probability=float(row.outbreak_probability),
        classification=OutbreakClassification(row.classification),
        model_version=row.model_version,
        observed_cases=float(row.observed_cases),
        baseline_cases=float(row.baseline_cases),
        assumptions=tuple(row.assumptions),
        drivers=tuple(row.drivers),
        feature_contributions=tuple(
            FeatureContribution(
                feature=str(item["feature"]),
                contribution=float(item["contribution"]),
                direction=str(item["direction"]),
            )
            for item in row.feature_contributions
        ),
        generated_at=row.generated_at or datetime.min,
    )

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from modules.territorial_risk.domain.explainability import FeatureContribution
from modules.territorial_risk.domain.repositories import RiskScoreRepository
from modules.territorial_risk.domain.risk_score import RiskClassification, RiskScore
from modules.territorial_risk.infrastructure.persistence.orm_models import TerritorialRiskScoreRow


def _score_id(
    territorial_code: str,
    period: str,
    definition_id: str,
    model_version: str,
) -> str:
    return f"{definition_id}:{territorial_code}:{period}:{model_version}"


def _row_to_domain(row: TerritorialRiskScoreRow) -> RiskScore:
    contributions = tuple(
        FeatureContribution(
            feature=item["feature"],
            value=float(item["value"]),
            contribution=float(item["contribution"]),
            description=item["description"],
        )
        for item in row.feature_contributions or []
    )
    return RiskScore(
        territorial_code=row.territorial_code,
        period=row.period,
        score=float(row.score),
        classification=RiskClassification(row.classification),
        model_version=row.model_version,
        observed_value=float(row.observed_value),
        baseline_value=float(row.baseline_value),
        indicator_definition_id=row.definition_id,
        assumptions=tuple(row.assumptions),
        drivers=tuple(row.drivers),
        feature_contributions=contributions,
        generated_at=row.generated_at,
    )


class SqlAlchemyRiskScoreRepository(RiskScoreRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(
        self,
        *,
        territorial_code: str,
        period: str,
        definition_id: str,
        model_version: str,
    ) -> RiskScore | None:
        row = self._session.get(
            TerritorialRiskScoreRow,
            _score_id(territorial_code, period, definition_id, model_version),
        )
        if row is None:
            return None
        return _row_to_domain(row)

    def save(self, risk_score: RiskScore) -> None:
        definition_id = risk_score.indicator_definition_id
        row = {
            "id": _score_id(
                risk_score.territorial_code,
                risk_score.period,
                definition_id,
                risk_score.model_version,
            ),
            "territorial_code": risk_score.territorial_code,
            "period": risk_score.period,
            "definition_id": definition_id,
            "score": risk_score.score,
            "classification": risk_score.classification.value,
            "model_version": risk_score.model_version,
            "observed_value": risk_score.observed_value,
            "baseline_value": risk_score.baseline_value,
            "assumptions": list(risk_score.assumptions),
            "drivers": list(risk_score.drivers),
            "feature_contributions": [
                {
                    "feature": item.feature,
                    "value": item.value,
                    "contribution": item.contribution,
                    "description": item.description,
                }
                for item in risk_score.feature_contributions
            ],
            "generated_at": risk_score.generated_at,
        }
        stmt = insert(TerritorialRiskScoreRow).values(row)
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                "territorial_code",
                "period",
                "definition_id",
                "model_version",
            ],
            set_={
                "score": stmt.excluded.score,
                "classification": stmt.excluded.classification,
                "observed_value": stmt.excluded.observed_value,
                "baseline_value": stmt.excluded.baseline_value,
                "assumptions": stmt.excluded.assumptions,
                "drivers": stmt.excluded.drivers,
                "feature_contributions": stmt.excluded.feature_contributions,
                "generated_at": stmt.excluded.generated_at,
            },
        )
        self._session.execute(stmt)
        self._session.commit()

    def list_for_period(
        self,
        *,
        period: str,
        definition_id: str,
        model_version: str,
        limit: int = 500,
    ) -> list[RiskScore]:
        rows = self._session.scalars(
            select(TerritorialRiskScoreRow)
            .where(
                TerritorialRiskScoreRow.period == period,
                TerritorialRiskScoreRow.definition_id == definition_id,
                TerritorialRiskScoreRow.model_version == model_version,
            )
            .order_by(TerritorialRiskScoreRow.score.desc())
            .limit(limit),
        ).all()
        return [_row_to_domain(row) for row in rows]

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from modules.territorial_risk.application.dto import PredictRiskQueryDto, RiskScoreReadDto
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase
from modules.territorial_risk.infrastructure.persistence.territorial_risk_data_adapter import (
    SqlAlchemyTerritorialRiskDataAdapter,
)

router = APIRouter(tags=["predict-risk"])


def get_predict_risk_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> PredictRiskUseCase:
    data_port = SqlAlchemyTerritorialRiskDataAdapter(session)
    return PredictRiskUseCase(data_port)


@router.get("/predict-risk", response_model=RiskScoreReadDto)
def predict_risk(
    query: Annotated[PredictRiskQueryDto, Query()],
    use_case: Annotated[PredictRiskUseCase, Depends(get_predict_risk_use_case)],
) -> RiskScoreReadDto:
    return use_case.execute(query)

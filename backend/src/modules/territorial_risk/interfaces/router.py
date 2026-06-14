from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from modules.territorial_risk.application.dto import (
    PredictRiskQueryDto,
    RiskScoreReadDto,
    TerritorialRiskMapPointDto,
    TerritorialRiskMapQueryDto,
)
from modules.territorial_risk.application.list_territorial_risk_map import (
    ListTerritorialRiskMapUseCase,
)
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase
from modules.territorial_risk.infrastructure.persistence.risk_score_repository import (
    SqlAlchemyRiskScoreRepository,
)
from modules.territorial_risk.infrastructure.persistence.territorial_risk_data_adapter import (
    SqlAlchemyTerritorialRiskDataAdapter,
)

router = APIRouter(tags=["predict-risk"])


def get_predict_risk_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> PredictRiskUseCase:
    data_port = SqlAlchemyTerritorialRiskDataAdapter(session)
    repository = SqlAlchemyRiskScoreRepository(session)
    return PredictRiskUseCase(data_port, repository)


def get_territorial_risk_map_use_case(
    session: Annotated[Session, Depends(get_db_session)],
    predict_risk_use_case: Annotated[PredictRiskUseCase, Depends(get_predict_risk_use_case)],
) -> ListTerritorialRiskMapUseCase:
    data_port = SqlAlchemyTerritorialRiskDataAdapter(session)
    return ListTerritorialRiskMapUseCase(data_port, predict_risk_use_case)


@router.get("/predict-risk", response_model=RiskScoreReadDto)
def predict_risk(
    query: Annotated[PredictRiskQueryDto, Query()],
    use_case: Annotated[PredictRiskUseCase, Depends(get_predict_risk_use_case)],
) -> RiskScoreReadDto:
    return use_case.execute(query)


@router.get("/territorial-risk-map", response_model=list[TerritorialRiskMapPointDto])
def list_territorial_risk_map(
    query: Annotated[TerritorialRiskMapQueryDto, Query()],
    use_case: Annotated[ListTerritorialRiskMapUseCase, Depends(get_territorial_risk_map_use_case)],
) -> list[TerritorialRiskMapPointDto]:
    return use_case.execute(query)

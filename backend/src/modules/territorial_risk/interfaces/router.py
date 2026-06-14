from typing import Annotated

from fastapi import APIRouter, Depends, Query

from modules.territorial_risk.application.dto import PredictRiskQueryDto, RiskScoreReadDto
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase

router = APIRouter(tags=["predict-risk"])


def get_predict_risk_use_case() -> PredictRiskUseCase:
    return PredictRiskUseCase()


@router.get("/predict-risk", response_model=RiskScoreReadDto)
def predict_risk(
    query: Annotated[PredictRiskQueryDto, Query()],
    use_case: Annotated[PredictRiskUseCase, Depends(get_predict_risk_use_case)],
) -> RiskScoreReadDto:
    return use_case.execute(query)

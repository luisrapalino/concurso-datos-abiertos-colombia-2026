from typing import Annotated

from fastapi import APIRouter, Depends, Query

from modules.prediction_engine.application.dto import (
    TerritorialTrendReadDto,
    TerritorialTrendsQueryDto,
)
from modules.prediction_engine.application.get_territorial_trends import GetTerritorialTrendsUseCase

router = APIRouter(tags=["territorial-trends"])


def get_territorial_trends_use_case() -> GetTerritorialTrendsUseCase:
    return GetTerritorialTrendsUseCase()


@router.get("/territorial-trends", response_model=TerritorialTrendReadDto)
def get_territorial_trends(
    query: Annotated[TerritorialTrendsQueryDto, Query()],
    use_case: Annotated[GetTerritorialTrendsUseCase, Depends(get_territorial_trends_use_case)],
) -> TerritorialTrendReadDto:
    return use_case.execute(query)

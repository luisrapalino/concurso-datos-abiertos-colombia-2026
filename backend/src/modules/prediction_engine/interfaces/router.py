from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from modules.epidemiological_surveillance.infrastructure.persistence.curated_observations_reader import (  # noqa: E501
    SqlAlchemyCuratedObservationsReader,
)
from modules.prediction_engine.application.dto import (
    TerritorialTrendReadDto,
    TerritorialTrendsQueryDto,
)
from modules.prediction_engine.application.get_territorial_trends import GetTerritorialTrendsUseCase
from modules.prediction_engine.infrastructure.forecasting.composite_forecast_service import (
    CompositeForecastService,
)

router = APIRouter(tags=["territorial-trends"])


def get_territorial_trends_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GetTerritorialTrendsUseCase:
    reader = SqlAlchemyCuratedObservationsReader(session)
    forecast_service = CompositeForecastService()
    return GetTerritorialTrendsUseCase(reader, forecast_service)


@router.get("/territorial-trends", response_model=TerritorialTrendReadDto)
def get_territorial_trends(
    query: Annotated[TerritorialTrendsQueryDto, Query()],
    use_case: Annotated[GetTerritorialTrendsUseCase, Depends(get_territorial_trends_use_case)],
) -> TerritorialTrendReadDto:
    return use_case.execute(query)

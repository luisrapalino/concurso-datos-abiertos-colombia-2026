from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from modules.health_indicators.application.dto import (
    HealthIndicatorReadDto,
    ListHealthIndicatorsQueryDto,
)
from modules.health_indicators.application.list_health_indicators import ListHealthIndicatorsUseCase
from modules.health_indicators.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyHealthIndicatorRepository,
)

router = APIRouter(tags=["health-indicators"])


def get_list_health_indicators_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> ListHealthIndicatorsUseCase:
    repository = SqlAlchemyHealthIndicatorRepository(session)
    return ListHealthIndicatorsUseCase(repository)


@router.get("/health-indicators", response_model=list[HealthIndicatorReadDto])
def list_health_indicators(
    query: Annotated[ListHealthIndicatorsQueryDto, Query()],
    use_case: Annotated[ListHealthIndicatorsUseCase, Depends(get_list_health_indicators_use_case)],
) -> list[HealthIndicatorReadDto]:
    return use_case.execute(query)

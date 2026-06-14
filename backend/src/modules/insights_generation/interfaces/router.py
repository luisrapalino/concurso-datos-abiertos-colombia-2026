from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from modules.epidemiological_surveillance.infrastructure.persistence.curated_observations_reader import (  # noqa: E501
    SqlAlchemyCuratedObservationsReader,
)
from modules.insights_generation.application.dto import InsightReadDto, ListInsightsQueryDto
from modules.insights_generation.application.generate_insights import GenerateInsightsUseCase
from modules.territorial_risk.infrastructure.persistence.territorial_risk_data_adapter import (
    SqlAlchemyTerritorialRiskDataAdapter,
)

router = APIRouter(tags=["insights"])


def get_generate_insights_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GenerateInsightsUseCase:
    reader = SqlAlchemyCuratedObservationsReader(session)
    risk_data = SqlAlchemyTerritorialRiskDataAdapter(session)
    return GenerateInsightsUseCase(reader, risk_data)


@router.get("/insights", response_model=list[InsightReadDto])
def list_insights(
    query: Annotated[ListInsightsQueryDto, Query()],
    use_case: Annotated[GenerateInsightsUseCase, Depends(get_generate_insights_use_case)],
) -> list[InsightReadDto]:
    return use_case.execute(query)

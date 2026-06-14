from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from modules.anomaly_detection.application.dto import AnomalyAlertPageDto, ListAnomaliesQueryDto
from modules.anomaly_detection.application.list_anomalies import ListAnomaliesUseCase
from modules.epidemiological_surveillance.infrastructure.persistence.curated_observations_reader import (  # noqa: E501
    SqlAlchemyCuratedObservationsReader,
)

router = APIRouter(tags=["anomalies"])


def get_list_anomalies_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> ListAnomaliesUseCase:
    reader = SqlAlchemyCuratedObservationsReader(session)
    return ListAnomaliesUseCase(reader)


@router.get("/anomalies", response_model=AnomalyAlertPageDto)
def list_anomalies(
    query: Annotated[ListAnomaliesQueryDto, Query()],
    use_case: Annotated[ListAnomaliesUseCase, Depends(get_list_anomalies_use_case)],
) -> AnomalyAlertPageDto:
    return use_case.execute(query)

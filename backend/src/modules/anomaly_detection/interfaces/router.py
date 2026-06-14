from typing import Annotated

from fastapi import APIRouter, Depends, Query

from modules.anomaly_detection.application.dto import AnomalyAlertPageDto, ListAnomaliesQueryDto
from modules.anomaly_detection.application.list_anomalies import ListAnomaliesUseCase

router = APIRouter(tags=["anomalies"])


def get_list_anomalies_use_case() -> ListAnomaliesUseCase:
    return ListAnomaliesUseCase()


@router.get("/anomalies", response_model=AnomalyAlertPageDto)
def list_anomalies(
    query: Annotated[ListAnomaliesQueryDto, Query()],
    use_case: Annotated[ListAnomaliesUseCase, Depends(get_list_anomalies_use_case)],
) -> AnomalyAlertPageDto:
    return use_case.execute(query)

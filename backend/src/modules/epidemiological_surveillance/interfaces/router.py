from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from modules.epidemiological_surveillance.application.dto import (
    DataFreshnessReadDto,
    DataQualityReadDto,
)
from modules.epidemiological_surveillance.application.get_data_freshness import (
    GetDataFreshnessUseCase,
)
from modules.epidemiological_surveillance.application.get_data_quality import GetDataQualityUseCase

router = APIRouter(tags=["data-freshness"])


def get_data_freshness_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GetDataFreshnessUseCase:
    return GetDataFreshnessUseCase(session)


def get_data_quality_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GetDataQualityUseCase:
    return GetDataQualityUseCase(session)


@router.get("/data-freshness", response_model=DataFreshnessReadDto)
def get_data_freshness(
    source_id: Annotated[str, Query(min_length=1)] = "datos-gov-mortality-indicators",
    use_case: Annotated[GetDataFreshnessUseCase, Depends(get_data_freshness_use_case)] = ...,
) -> DataFreshnessReadDto:
    return use_case.execute(source_id)


@router.get("/data-quality", response_model=DataQualityReadDto)
def get_data_quality(
    source_id: Annotated[str, Query(min_length=1)] = "datos-gov-mortality-indicators",
    use_case: Annotated[GetDataQualityUseCase, Depends(get_data_quality_use_case)] = ...,
) -> DataQualityReadDto:
    return use_case.execute(source_id=source_id)

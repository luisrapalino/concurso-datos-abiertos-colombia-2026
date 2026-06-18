from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from modules.epidemiological_surveillance.application.dto import (
    DataDriftReadDto,
    DataFreshnessReadDto,
    DataQualityReadDto,
)
from modules.epidemiological_surveillance.application.get_data_drift import GetDataDriftUseCase
from modules.epidemiological_surveillance.application.get_data_freshness import (
    GetDataFreshnessUseCase,
)
from modules.epidemiological_surveillance.application.bias_dto import BiasAnalysisReadDto
from modules.epidemiological_surveillance.application.get_bias_analysis import GetBiasAnalysisUseCase
from modules.epidemiological_surveillance.application.municipality_dto import MunicipalityReadDto
from modules.epidemiological_surveillance.application.get_data_quality import GetDataQualityUseCase
from modules.epidemiological_surveillance.application.search_municipalities import (
    SearchMunicipalitiesUseCase,
)
from modules.epidemiological_surveillance.application.list_municipal_variable_datasets import (
    ListMunicipalVariableDatasetsUseCase,
)
from modules.epidemiological_surveillance.application.municipal_variable_dataset_dto import (
    MunicipalVariableDatasetDto,
)
from modules.epidemiological_surveillance.application.dataset_dto import DatasetReadDto
from modules.epidemiological_surveillance.application.list_datasets import ListDatasetsUseCase
from modules.epidemiological_surveillance.application.sivigila_event_dto import SivigilaEventReadDto
from config.settings import get_settings
from shared.divipola_catalog import DivipolaCatalog
from shared.sivigila_events import TRANSMISSIBLE_SIVIGILA_EVENTS

router = APIRouter(tags=["data-freshness"])


def get_data_freshness_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GetDataFreshnessUseCase:
    return GetDataFreshnessUseCase(session)


def get_data_quality_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GetDataQualityUseCase:
    return GetDataQualityUseCase(session)


def get_data_drift_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GetDataDriftUseCase:
    return GetDataDriftUseCase(session)


def get_bias_analysis_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GetBiasAnalysisUseCase:
    return GetBiasAnalysisUseCase(session)


def get_search_municipalities_use_case() -> SearchMunicipalitiesUseCase:
    return SearchMunicipalitiesUseCase()


def get_list_datasets_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> ListDatasetsUseCase:
    return ListDatasetsUseCase(session)


def get_list_municipal_variable_datasets_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> ListMunicipalVariableDatasetsUseCase:
    settings = get_settings()
    catalog = DivipolaCatalog.from_file(settings.divipola_catalog_path)
    return ListMunicipalVariableDatasetsUseCase(session, catalog=catalog)


@router.get("/datasets", response_model=list[DatasetReadDto])
def list_datasets(
    use_case: Annotated[ListDatasetsUseCase, Depends(get_list_datasets_use_case)] = ...,
) -> list[DatasetReadDto]:
    return use_case.execute()


@router.get("/municipal-datasets", response_model=list[MunicipalVariableDatasetDto])
def list_municipal_variable_datasets(
    use_case: Annotated[
        ListMunicipalVariableDatasetsUseCase,
        Depends(get_list_municipal_variable_datasets_use_case),
    ] = ...,
) -> list[MunicipalVariableDatasetDto]:
    return use_case.execute()


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


@router.get("/data-drift", response_model=DataDriftReadDto)
def get_data_drift(
    definition_id: Annotated[str, Query(min_length=1)] = "general-mortality-rate",
    use_case: Annotated[GetDataDriftUseCase, Depends(get_data_drift_use_case)] = ...,
) -> DataDriftReadDto:
    return use_case.execute(definition_id=definition_id)


@router.get("/bias-analysis", response_model=BiasAnalysisReadDto)
def get_bias_analysis(
    period: Annotated[str, Query(min_length=1)],
    definition_id: Annotated[str, Query(min_length=1)] = "general-mortality-rate",
    use_case: Annotated[GetBiasAnalysisUseCase, Depends(get_bias_analysis_use_case)] = ...,
) -> BiasAnalysisReadDto:
    return use_case.execute(period=period, definition_id=definition_id)


@router.get("/municipalities/featured", response_model=list[MunicipalityReadDto])
def list_featured_municipalities(
    use_case: Annotated[SearchMunicipalitiesUseCase, Depends(get_search_municipalities_use_case)] = ...,
) -> list[MunicipalityReadDto]:
    return use_case.list_featured()


@router.get("/sivigila-events", response_model=list[SivigilaEventReadDto])
def list_sivigila_events() -> list[SivigilaEventReadDto]:
    return [
        SivigilaEventReadDto(
            code=event.code,
            definition_id=event.definition_id,
            name=event.name,
            slug=event.slug,
        )
        for event in TRANSMISSIBLE_SIVIGILA_EVENTS
    ]


@router.get("/municipalities", response_model=list[MunicipalityReadDto])
def search_municipalities(
    search: Annotated[str, Query(min_length=1, max_length=80)],
    limit: Annotated[int, Query(ge=1, le=25)] = 8,
    use_case: Annotated[SearchMunicipalitiesUseCase, Depends(get_search_municipalities_use_case)] = ...,
) -> list[MunicipalityReadDto]:
    return use_case.execute(search=search, limit=limit)


@router.get("/municipalities/{territorial_code}", response_model=MunicipalityReadDto)
def get_municipality(
    territorial_code: Annotated[str, Path(min_length=5, max_length=5, pattern=r"^\d{5}$")],
    use_case: Annotated[SearchMunicipalitiesUseCase, Depends(get_search_municipalities_use_case)] = ...,
) -> MunicipalityReadDto:
    municipality = use_case.get_by_code(territorial_code)
    if municipality is None:
        raise HTTPException(status_code=404, detail="Municipality not found")
    return municipality

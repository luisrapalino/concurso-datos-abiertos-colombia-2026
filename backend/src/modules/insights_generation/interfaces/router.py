from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from config.settings import get_settings
from modules.epidemiological_surveillance.application.get_data_drift import GetDataDriftUseCase
from modules.insights_generation.application.dto import InsightReadDto, ListInsightsQueryDto
from modules.insights_generation.application.generate_insights import GenerateInsightsUseCase
from modules.insights_generation.application.get_territorial_report import GetTerritorialReportUseCase
from modules.insights_generation.application.territorial_report_dto import (
    TerritorialReportQueryDto,
    TerritorialReportReadDto,
)
from modules.epidemiological_surveillance.infrastructure.persistence.curated_observations_reader import (  # noqa: E501
    SqlAlchemyCuratedObservationsReader,
)
from modules.territorial_risk.application.dto import PredictRiskQueryDto
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase
from modules.territorial_risk.infrastructure.ml.file_promoted_model_adapter import (
    FilePromotedRiskModelAdapter,
)
from modules.territorial_risk.infrastructure.persistence.risk_score_repository import (
    SqlAlchemyRiskScoreRepository,
)
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


def get_predict_risk_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> PredictRiskUseCase:
    data_port = SqlAlchemyTerritorialRiskDataAdapter(session)
    repository = SqlAlchemyRiskScoreRepository(session)
    promoted_model = FilePromotedRiskModelAdapter(get_settings())
    return PredictRiskUseCase(data_port, repository, promoted_model)


def get_data_drift_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> GetDataDriftUseCase:
    return GetDataDriftUseCase(session)


def get_territorial_report_use_case(
    predict_risk_use_case: Annotated[PredictRiskUseCase, Depends(get_predict_risk_use_case)],
    generate_insights_use_case: Annotated[
        GenerateInsightsUseCase,
        Depends(get_generate_insights_use_case),
    ],
    get_data_drift_use_case: Annotated[GetDataDriftUseCase, Depends(get_data_drift_use_case)],
) -> GetTerritorialReportUseCase:
    return GetTerritorialReportUseCase(
        predict_risk_use_case,
        generate_insights_use_case,
        get_data_drift_use_case,
    )


@router.get("/insights", response_model=list[InsightReadDto])
def list_insights(
    query: Annotated[ListInsightsQueryDto, Query()],
    use_case: Annotated[GenerateInsightsUseCase, Depends(get_generate_insights_use_case)],
) -> list[InsightReadDto]:
    return use_case.execute(query)


@router.get("/territorial-report", response_model=TerritorialReportReadDto)
def get_territorial_report(
    query: Annotated[TerritorialReportQueryDto, Query()],
    use_case: Annotated[GetTerritorialReportUseCase, Depends(get_territorial_report_use_case)],
) -> TerritorialReportReadDto:
    return use_case.execute(query)

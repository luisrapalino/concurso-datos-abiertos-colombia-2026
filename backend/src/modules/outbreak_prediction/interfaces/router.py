from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from config.settings import get_settings
from modules.outbreak_prediction.application.dto import (
    OutbreakAlertDto,
    OutbreakAlertsQueryDto,
    OutbreakMapPointDto,
    OutbreakMapQueryDto,
    OutbreakPredictionReadDto,
    PredictOutbreakQueryDto,
)
from modules.outbreak_prediction.application.list_outbreak_alerts import ListOutbreakAlertsUseCase
from modules.outbreak_prediction.application.list_outbreak_map import ListOutbreakMapUseCase
from modules.outbreak_prediction.application.predict_outbreak import PredictOutbreakUseCase
from modules.outbreak_prediction.infrastructure.ml.file_promoted_outbreak_model_adapter import (
    FilePromotedOutbreakModelAdapter,
)
from modules.outbreak_prediction.infrastructure.outbreak_data_adapter import (
    SqlAlchemyOutbreakDataAdapter,
)
from modules.outbreak_prediction.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyOutbreakPredictionRepository,
)

router = APIRouter(tags=["outbreak-prediction"])


def get_predict_outbreak_use_case(
    session: Annotated[Session, Depends(get_db_session)],
) -> PredictOutbreakUseCase:
    return PredictOutbreakUseCase(
        SqlAlchemyOutbreakDataAdapter(session),
        SqlAlchemyOutbreakPredictionRepository(session),
        FilePromotedOutbreakModelAdapter(get_settings()),
    )


def get_list_outbreak_map_use_case(
    session: Annotated[Session, Depends(get_db_session)],
    predict_outbreak_use_case: Annotated[
        PredictOutbreakUseCase,
        Depends(get_predict_outbreak_use_case),
    ],
) -> ListOutbreakMapUseCase:
    return ListOutbreakMapUseCase(
        SqlAlchemyOutbreakDataAdapter(session),
        predict_outbreak_use_case,
    )


def get_list_outbreak_alerts_use_case(
    session: Annotated[Session, Depends(get_db_session)],
    predict_outbreak_use_case: Annotated[
        PredictOutbreakUseCase,
        Depends(get_predict_outbreak_use_case),
    ],
) -> ListOutbreakAlertsUseCase:
    return ListOutbreakAlertsUseCase(
        SqlAlchemyOutbreakDataAdapter(session),
        predict_outbreak_use_case,
    )


@router.get("/outbreak-predictions", response_model=OutbreakPredictionReadDto)
def predict_outbreak(
    query: Annotated[PredictOutbreakQueryDto, Query()],
    use_case: Annotated[PredictOutbreakUseCase, Depends(get_predict_outbreak_use_case)],
) -> OutbreakPredictionReadDto:
    return use_case.execute(query)


@router.get("/outbreak-map", response_model=list[OutbreakMapPointDto])
def list_outbreak_map(
    query: Annotated[OutbreakMapQueryDto, Query()],
    use_case: Annotated[ListOutbreakMapUseCase, Depends(get_list_outbreak_map_use_case)],
) -> list[OutbreakMapPointDto]:
    return use_case.execute(query)


@router.get("/outbreak-alerts", response_model=list[OutbreakAlertDto])
def list_outbreak_alerts(
    query: Annotated[OutbreakAlertsQueryDto, Query()],
    use_case: Annotated[ListOutbreakAlertsUseCase, Depends(get_list_outbreak_alerts_use_case)],
) -> list[OutbreakAlertDto]:
    return use_case.execute(query)

from modules.anomaly_detection.application.dto import (
    AnomalyAlertPageDto,
    AnomalyAlertReadDto,
    ListAnomaliesQueryDto,
)
from modules.anomaly_detection.domain.detection import AnomalyAlert, evaluate_observation
from modules.anomaly_detection.domain.repositories import CuratedObservationsReader
from modules.outbreak_prediction.domain.outbreak_prediction import DENGUE_DEFINITION_ID
from shared.pagination import PaginatedResponse


class ListAnomaliesUseCase:
    """Detects territorial anomalies from curated transmissible disease observations."""

    def __init__(self, reader: CuratedObservationsReader) -> None:
        self._reader = reader

    def execute(self, query: ListAnomaliesQueryDto) -> AnomalyAlertPageDto:
        territorial_code = str(query.territorial_code) if query.territorial_code else None
        definition_id = query.definition_id or DENGUE_DEFINITION_ID
        observations = self._reader.list_observations_with_period_median(
            definition_id,
            territorial_code=territorial_code,
        )

        alerts = [
            alert
            for observation in observations
            if (alert := evaluate_observation(observation)) is not None
        ]

        page = PaginatedResponse.from_items(
            [_to_dto(alert) for alert in alerts],
            page=query.page,
            page_size=query.page_size,
            total_items=len(alerts),
        )
        return AnomalyAlertPageDto(
            items=page.items,
            page=page.page,
            page_size=page.page_size,
            total_items=page.total_items,
            total_pages=page.total_pages,
        )


def _to_dto(alert: AnomalyAlert) -> AnomalyAlertReadDto:
    return AnomalyAlertReadDto(
        id=alert.id,
        territorial_code=alert.territorial_code,
        indicator_id=alert.indicator_id,
        indicator_name=alert.indicator_name,
        detected_on=alert.detected_on,
        severity=alert.severity,
        description=alert.description,
        baseline_value=alert.baseline_value,
        observed_value=alert.observed_value,
    )

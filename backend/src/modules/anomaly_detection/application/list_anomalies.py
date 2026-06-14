from datetime import date

from modules.anomaly_detection.application.dto import (
    AnomalyAlertPageDto,
    AnomalyAlertReadDto,
    AnomalySeverity,
    ListAnomaliesQueryDto,
)
from shared.pagination import PaginatedResponse


class ListAnomaliesUseCase:
    """Returns stub anomaly alerts until detection pipelines are wired."""

    _STUB_ALERTS: tuple[AnomalyAlertReadDto, ...] = (
        AnomalyAlertReadDto(
            id="stub-anomaly-001",
            territorial_code="05",
            indicator_id="stub-mortality-rate",
            indicator_name="Crude mortality rate (placeholder)",
            detected_on=date(2024, 3, 15),
            severity=AnomalySeverity.MEDIUM,
            description="Observed rate exceeds rolling 8-week baseline (stub).",
            baseline_value=12.4,
            observed_value=18.9,
        ),
        AnomalyAlertReadDto(
            id="stub-anomaly-002",
            territorial_code="05001",
            indicator_id="stub-mortality-rate",
            indicator_name="Crude mortality rate (placeholder)",
            detected_on=date(2024, 4, 2),
            severity=AnomalySeverity.HIGH,
            description="Sudden week-over-week increase flagged for manual review (stub).",
            baseline_value=10.1,
            observed_value=21.3,
        ),
    )

    def execute(self, query: ListAnomaliesQueryDto) -> AnomalyAlertPageDto:
        filtered = [
            alert
            for alert in self._STUB_ALERTS
            if query.territorial_code is None or alert.territorial_code == query.territorial_code
        ]
        page = PaginatedResponse.from_items(
            filtered,
            page=query.page,
            page_size=query.page_size,
            total_items=len(filtered),
        )
        return AnomalyAlertPageDto(
            items=page.items,
            page=page.page,
            page_size=page.page_size,
            total_items=page.total_items,
            total_pages=page.total_pages,
        )

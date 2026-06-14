from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from modules.anomaly_detection.domain.detection import ObservationWithBaseline


@dataclass(frozen=True, slots=True)
class TerritorialSeriesPoint:
    period: str
    value: Decimal


class CuratedObservationsReader(Protocol):
    def list_observations_with_period_median(
        self,
        definition_id: str,
        *,
        territorial_code: str | None = None,
    ) -> list[ObservationWithBaseline]:
        """Return observations joined with the national median for each period."""

    def list_territorial_series(
        self,
        territorial_code: str,
        definition_id: str,
    ) -> tuple[str, list[TerritorialSeriesPoint]]:
        """Return indicator name and ordered historical points for a territory."""

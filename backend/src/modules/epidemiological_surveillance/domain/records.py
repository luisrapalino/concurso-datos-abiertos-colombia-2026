from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class RawHealthIndicatorRecord:
    """Normalized row extracted from open data sources before persistence."""

    territorial_code: str
    territory_name: str
    source_indicator_key: str
    period: str
    value: Decimal


@dataclass(frozen=True, slots=True)
class RawMortalityIndicatorRecord:
    """Annual mortality indicator row (legacy alias for health indicator records)."""

    territorial_code: str
    territory_name: str
    source_indicator_key: str
    year: int
    value: Decimal

    def to_health_record(self, *, period: str | None = None) -> RawHealthIndicatorRecord:
        from modules.epidemiological_surveillance.application.normalization import annual_period

        return RawHealthIndicatorRecord(
            territorial_code=self.territorial_code,
            territory_name=self.territory_name,
            source_indicator_key=self.source_indicator_key,
            period=period or annual_period(self.year),
            value=self.value,
        )


@dataclass(frozen=True, slots=True)
class CuratedObservation:
    """Domain representation of a persisted health indicator observation."""

    id: str
    definition_id: str
    name: str
    measurement_unit: str
    territorial_code: str
    period: str
    value: Decimal
    source_id: str
    ingested_at: datetime | None

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class RawMortalityIndicatorRecord:
    """Normalized row extracted from datos.gov.co before persistence."""

    territorial_code: str
    territory_name: str
    source_indicator_key: str
    year: int
    value: Decimal


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

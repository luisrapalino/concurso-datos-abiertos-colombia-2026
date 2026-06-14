from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class HealthIndicator:
    """Curated territorial health indicator observation."""

    id: str
    definition_id: str
    name: str
    territorial_code: str
    period: str
    value: Decimal
    measurement_unit: str
    source_id: str
    ingested_at: datetime | None

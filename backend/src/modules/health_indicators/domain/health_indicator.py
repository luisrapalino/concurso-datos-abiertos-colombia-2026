from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HealthIndicator:
    """Territorial health indicator definition (domain entity)."""

    id: str
    name: str
    territorial_code: str | None
    measurement_unit: str | None

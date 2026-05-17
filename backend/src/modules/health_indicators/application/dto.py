from pydantic import BaseModel, Field


class HealthIndicatorReadDto(BaseModel):
    """Read model returned by the list health indicators use case (stub)."""

    id: str = Field(description="Stable identifier for the indicator definition.")
    name: str
    territorial_code: str | None = None
    measurement_unit: str | None = None

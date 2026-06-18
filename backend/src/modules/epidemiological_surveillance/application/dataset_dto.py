from datetime import datetime

from pydantic import BaseModel, Field


class DatasetReadDto(BaseModel):
    definition_id: str
    name: str
    source_id: str
    source_name: str
    provider: str
    portal_url: str
    api_url: str
    measurement_unit: str
    granularity: str
    records_ingested: int = 0
    municipalities_count: int = 0
    latest_period: str | None = None
    last_ingestion_at: datetime | None = None
    coverage_note: str = Field(
        default="Cobertura piloto: Medellín, Bogotá, Barranquilla y Cali.",
    )

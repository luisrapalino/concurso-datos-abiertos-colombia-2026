from datetime import datetime

from pydantic import BaseModel, Field

from shared.period import Period


class TerritorialCatalogMetadataDto(BaseModel):
    source_id: str
    synced_at: datetime | None = None
    municipality_count: int


class DataFreshnessReadDto(BaseModel):
    source_id: str
    source_name: str
    last_successful_ingestion_at: datetime | None = None
    records_upserted: int | None = None
    latest_period_available: Period | None = None
    coverage_note: str = Field(
        default="Coverage depends on published open data; gaps must be interpreted cautiously.",
    )


class DataQualityReadDto(BaseModel):
    source_id: str
    total_observations: int
    distinct_territories: int
    distinct_periods: int
    periods_available: list[Period]
    latest_ingestion_at: datetime | None = None
    temporal_coverage_note: str
    territorial_catalog: TerritorialCatalogMetadataDto

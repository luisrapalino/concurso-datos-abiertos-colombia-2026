from dataclasses import dataclass
from typing import Protocol

from modules.epidemiological_surveillance.domain.records import (
    RawHealthIndicatorRecord,
    RawMortalityIndicatorRecord,
)


@dataclass(frozen=True, slots=True)
class IngestionResult:
    run_id: str
    records_upserted: int
    records_rejected: int = 0
    rejected_territorial_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SyncIngestionResult:
    run_id: str
    records_upserted: int
    records_rejected: int
    batches_processed: int
    years_processed: tuple[int, ...]
    rejected_territorial_codes: tuple[str, ...] = ()


class HealthIndicatorsSourceClient(Protocol):
    def fetch_records(
        self,
        *,
        year: int | None = None,
        territorial_code: str | None = None,
        limit: int = 5000,
        offset: int = 0,
    ) -> list[RawHealthIndicatorRecord]:
        """Fetch normalized health indicator records from the external source."""


class MortalityIndicatorsSourceClient(Protocol):
    def fetch_general_mortality_records(
        self,
        *,
        year: int | None = None,
        limit: int = 5000,
        offset: int = 0,
    ) -> list[RawMortalityIndicatorRecord]:
        """Fetch normalized mortality indicator records from the external source."""


class IngestionRepository(Protocol):
    def begin_run(self, source_id: str) -> str:
        """Create a running ingestion run and return its identifier."""

    def complete_run(self, run_id: str, *, records_upserted: int) -> None:
        """Mark an ingestion run as succeeded."""

    def fail_run(self, run_id: str, error_message: str) -> None:
        """Mark an ingestion run as failed."""

    def upsert_observations(
        self,
        *,
        run_id: str,
        source_id: str,
        definition_id: str,
        records: list[RawHealthIndicatorRecord | RawMortalityIndicatorRecord],
    ) -> int:
        """Persist observations idempotently and return upsert count."""

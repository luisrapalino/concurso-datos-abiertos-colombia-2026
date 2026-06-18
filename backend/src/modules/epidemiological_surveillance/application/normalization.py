from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class IngestHealthIndicatorsCommand:
    source_id: str
    definition_id: str
    source_indicator_key: str
    year: int | None = None
    years: tuple[int, ...] | None = None
    limit: int = 5000
    dry_run: bool = False
    validate_territorial_codes: bool = True


@dataclass(frozen=True, slots=True)
class SyncIngestHealthIndicatorsCommand:
    """Incremental open-data sync: paginate by year and optionally by municipality."""

    source_id: str
    definition_id: str
    source_indicator_key: str
    sync_strategy: str
    batch_size: int = 1000
    start_year: int | None = None
    end_year: int = 2015
    territorial_codes: tuple[str, ...] | None = None
    dry_run: bool = False
    validate_territorial_codes: bool = True
    max_batches: int | None = None


IngestMortalityIndicatorsCommand = IngestHealthIndicatorsCommand


def annual_period(year: int) -> str:
    return f"{year:04d}-01"


def epidemiological_week_period(year: int, week: int) -> str:
    return f"{year:04d}-W{week:02d}"


def observation_id(definition_id: str, territorial_code: str, period: str) -> str:
    return f"{definition_id}:{territorial_code}:{period}"


def normalize_territorial_code(raw_code: str) -> str:
    code = raw_code.strip()
    if not code.isdigit():
        msg = f"Territorial code must be numeric: {raw_code!r}"
        raise ValueError(msg)
    return code.zfill(5) if len(code) <= 5 else code


def normalize_indicator_value(raw_value: str | float) -> Decimal:
    return Decimal(str(raw_value))

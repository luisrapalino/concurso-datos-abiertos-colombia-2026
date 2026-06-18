from modules.epidemiological_surveillance.domain.records import (
    RawHealthIndicatorRecord,
    RawMortalityIndicatorRecord,
)
from shared.divipola_catalog import TerritorialCatalog, TerritorialValidationSummary

TerritorialRecord = RawHealthIndicatorRecord | RawMortalityIndicatorRecord


def partition_records_by_catalog(
    records: list[TerritorialRecord],
    catalog: TerritorialCatalog,
    *,
    max_rejected_samples: int = 20,
) -> tuple[list[TerritorialRecord], TerritorialValidationSummary]:
    accepted: list[TerritorialRecord] = []
    rejected_codes: list[str] = []

    for record in records:
        if catalog.is_valid_municipality(record.territorial_code):
            accepted.append(record)
            continue
        if len(rejected_codes) < max_rejected_samples:
            rejected_codes.append(record.territorial_code)

    return (
        accepted,
        TerritorialValidationSummary(
            accepted_count=len(accepted),
            rejected_count=len(records) - len(accepted),
            rejected_territorial_codes=tuple(rejected_codes),
        ),
    )

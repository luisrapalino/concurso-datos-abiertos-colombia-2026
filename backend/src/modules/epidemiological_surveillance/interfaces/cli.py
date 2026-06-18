"""CLI for epidemiological data ingestion."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from config.settings import get_settings
from infrastructure.persistence.database import dispose_engine, get_session, init_engine
from modules.epidemiological_surveillance.application.ingest_health_indicators import (
    IngestHealthIndicatorsUseCase,
)
from modules.epidemiological_surveillance.application.sync_ingest_health_indicators import (
    SyncIngestHealthIndicatorsUseCase,
)
from modules.epidemiological_surveillance.application.sync_municipal_indicators import (
    SyncMunicipalIndicatorsUseCase,
    default_municipal_sync_command,
)
from modules.epidemiological_surveillance.application.municipal_dataset_resolver import (
    MunicipalDatasetResolver,
)
from modules.epidemiological_surveillance.application.normalization import (
    IngestHealthIndicatorsCommand,
    SyncIngestHealthIndicatorsCommand,
)
from modules.epidemiological_surveillance.infrastructure.persistence.sqlalchemy_ingestion_repository import (  # noqa: E501
    SqlAlchemyIngestionRepository,
)
from modules.epidemiological_surveillance.infrastructure.sources.air_quality_client import (
    AirQualityClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.municipal_dataset_fetcher import (
    MunicipalDatasetFetcher,
)
from modules.epidemiological_surveillance.infrastructure.sources.client_adapters import (
    MortalityIndicatorsClientAdapter,
)
from modules.epidemiological_surveillance.infrastructure.sources.datos_gov_co_client import (
    GENERAL_MORTALITY_INDICATOR,
    INSTITUTIONAL_BIRTHS_INDICATOR,
    DatosGovCoMortalityClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.sivigila_client import (
    SivigilaSurveillanceClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.vaccination_client import (
    PENTAVALENT_VACCINE,
    VaccinationCoverageClient,
)
from shared.divipola_catalog import DivipolaCatalog
from shared.featured_municipalities import FEATURED_MUNICIPALITY_CODES
from shared.sivigila_events import TRANSMISSIBLE_SIVIGILA_EVENTS

SOURCE_DATOS_GOV_MORTALITY = "datos-gov-mortality-indicators"
DEFINITION_GENERAL_MORTALITY = "general-mortality-rate"
SOURCE_SIVIGILA = "datos-gov-sivigila"
SOURCE_VACCINATION = "datos-gov-vaccination-coverage"
DEFINITION_VACCINATION = "dpta-penta-vaccination-coverage"
SOURCE_AIR_QUALITY = "datos-gov-air-quality"
DEFINITION_PM25 = "pm25-annual-mean"
DEFINITION_HEALTH_ACCESS = "institutional-births-coverage"

SOURCE_REGISTRY: dict[str, dict[str, str]] = {
    SOURCE_DATOS_GOV_MORTALITY: {
        "source_id": SOURCE_DATOS_GOV_MORTALITY,
        "definition_id": DEFINITION_GENERAL_MORTALITY,
        "source_indicator_key": GENERAL_MORTALITY_INDICATOR,
        "client_type": "mortality",
        "sync_strategy": "per_municipality",
    },
    "datos-gov-vaccination-coverage": {
        "source_id": SOURCE_VACCINATION,
        "definition_id": DEFINITION_VACCINATION,
        "source_indicator_key": "PENTA3",
        "client_type": "vaccination",
        "sync_strategy": "per_municipality",
    },
    "datos-gov-air-quality": {
        "source_id": SOURCE_AIR_QUALITY,
        "definition_id": DEFINITION_PM25,
        "source_indicator_key": "pm25",
        "client_type": "air_quality",
        "sync_strategy": "per_municipality",
    },
    "datos-gov-health-access": {
        "source_id": SOURCE_DATOS_GOV_MORTALITY,
        "definition_id": DEFINITION_HEALTH_ACCESS,
        "source_indicator_key": INSTITUTIONAL_BIRTHS_INDICATOR,
        "client_type": "mortality",
        "sync_strategy": "per_municipality",
    },
}

for _event in TRANSMISSIBLE_SIVIGILA_EVENTS:
    SOURCE_REGISTRY[f"datos-gov-sivigila-{_event.slug}"] = {
        "source_id": SOURCE_SIVIGILA,
        "definition_id": _event.definition_id,
        "source_indicator_key": _event.code,
        "client_type": "sivigila",
        "sync_strategy": "per_municipality",
    }

SYNC_SOURCE_ORDER: tuple[str, ...] = tuple(
    f"datos-gov-sivigila-{event.slug}" for event in TRANSMISSIBLE_SIVIGILA_EVENTS
) + (
    "datos-gov-vaccination-coverage",
    "datos-gov-health-access",
    "datos-gov-air-quality",
    "datos-gov-mortality-indicators",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Epidemiological surveillance ingestion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Run a batch ingestion job")
    ingest_parser.add_argument(
        "source",
        choices=sorted(SOURCE_REGISTRY.keys()),
        help="Registered open data source identifier",
    )
    ingest_parser.add_argument("--year", type=int, default=None, help="Restrict to a calendar year")
    ingest_parser.add_argument(
        "--years",
        type=str,
        default=None,
        help="Comma-separated calendar years (e.g. 2018,2019,2020). Overrides --year.",
    )
    ingest_parser.add_argument(
        "--limit",
        type=int,
        default=5000,
        help="Maximum number of records to fetch",
    )
    ingest_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and count records without writing to the database",
    )
    ingest_parser.add_argument(
        "--skip-territorial-validation",
        action="store_true",
        help="Skip DANE DIVIPOLA municipality code validation",
    )

    sync_parser = subparsers.add_parser(
        "ingest-sync",
        help="Incremental batch sync from open data (year-by-year pagination)",
    )
    sync_parser.add_argument(
        "source",
        choices=sorted(SOURCE_REGISTRY.keys()),
        help="Registered open data source identifier",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Records per API request (default from settings, typically 1000)",
    )
    sync_parser.add_argument(
        "--start-year",
        type=int,
        default=None,
        help="Most recent year to sync (default: current calendar year)",
    )
    sync_parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        help="Oldest year to sync (default from settings, typically 2015)",
    )
    sync_parser.add_argument(
        "--all-municipalities",
        action="store_true",
        help="Sync all DIVIPOLA municipalities (default: 4 pilot cities)",
    )
    sync_parser.add_argument(
        "--territorial-codes",
        type=str,
        default=None,
        help="Comma-separated DANE codes (overrides pilot default)",
    )
    sync_parser.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Stop after N API batches (useful for smoke tests)",
    )
    sync_parser.add_argument("--dry-run", action="store_true")
    sync_parser.add_argument("--skip-territorial-validation", action="store_true")

    sync_all_parser = subparsers.add_parser(
        "ingest-sync-all",
        help="Run ingest-sync for all competition sources in recommended order",
    )
    sync_all_parser.add_argument("--batch-size", type=int, default=None)
    sync_all_parser.add_argument("--start-year", type=int, default=None)
    sync_all_parser.add_argument("--end-year", type=int, default=None)
    sync_all_parser.add_argument("--all-municipalities", action="store_true")
    sync_all_parser.add_argument("--territorial-codes", type=str, default=None)
    sync_all_parser.add_argument("--max-batches", type=int, default=None)
    sync_all_parser.add_argument("--dry-run", action="store_true")
    sync_all_parser.add_argument("--skip-territorial-validation", action="store_true")

    sync_municipal_parser = subparsers.add_parser(
        "ingest-sync-municipal",
        help="Sync pilot municipalities variable-by-variable with best dataset resolution",
    )
    sync_municipal_parser.add_argument("--batch-size", type=int, default=None)
    sync_municipal_parser.add_argument("--start-year", type=int, default=None)
    sync_municipal_parser.add_argument("--end-year", type=int, default=None)
    sync_municipal_parser.add_argument("--territorial-codes", type=str, default=None)
    sync_municipal_parser.add_argument("--definition-ids", type=str, default=None)
    sync_municipal_parser.add_argument("--max-batches", type=int, default=None)
    sync_municipal_parser.add_argument("--dry-run", action="store_true")
    sync_municipal_parser.add_argument("--skip-territorial-validation", action="store_true")
    return parser


def _parse_years(raw_years: str | None) -> tuple[int, ...] | None:
    if not raw_years:
        return None
    years = tuple(int(value.strip()) for value in raw_years.split(",") if value.strip())
    if not years:
        msg = "At least one year must be provided when using --years."
        raise ValueError(msg)
    return years


def _build_source_client(
    registry: dict[str, str],
    *,
    catalog: DivipolaCatalog | None,
) -> Any:
    client_type = registry["client_type"]
    if client_type == "mortality":
        return MortalityIndicatorsClientAdapter(
            DatosGovCoMortalityClient(source_indicator_key=registry["source_indicator_key"]),
        )
    if client_type == "sivigila":
        return SivigilaSurveillanceClient(event_code=registry["source_indicator_key"])
    if client_type == "vaccination":
        if catalog is None:
            msg = "DIVIPOLA catalog is required for vaccination coverage ingestion."
            raise ValueError(msg)
        return VaccinationCoverageClient(
            vaccine_name=registry["source_indicator_key"],
            territorial_catalog=catalog,
        )
    if client_type == "air_quality":
        if catalog is None:
            msg = "DIVIPOLA catalog is required for air quality ingestion."
            raise ValueError(msg)
        return AirQualityClient(territorial_catalog=catalog)
    msg = f"Unsupported client type: {client_type}"
    raise ValueError(msg)


def _parse_territorial_codes(raw_codes: str | None) -> tuple[str, ...] | None:
    if not raw_codes:
        return None
    codes = tuple(code.strip().zfill(5) for code in raw_codes.split(",") if code.strip())
    return codes or None


def _resolve_sync_territorial_codes(args: argparse.Namespace) -> tuple[str, ...] | None:
    explicit = _parse_territorial_codes(getattr(args, "territorial_codes", None))
    if explicit is not None:
        return explicit
    if getattr(args, "all_municipalities", False):
        return None
    return FEATURED_MUNICIPALITY_CODES


def _build_sync_command(
    registry: dict[str, str],
    args: argparse.Namespace,
    settings: Any,
) -> SyncIngestHealthIndicatorsCommand:
    sync_strategy = registry["sync_strategy"]
    territorial_codes = _resolve_sync_territorial_codes(args)
    if sync_strategy != "per_municipality":
        territorial_codes = None

    return SyncIngestHealthIndicatorsCommand(
        source_id=registry["source_id"],
        definition_id=registry["definition_id"],
        source_indicator_key=registry["source_indicator_key"],
        sync_strategy=sync_strategy,
        batch_size=args.batch_size or settings.ingestion_batch_size,
        start_year=args.start_year,
        end_year=args.end_year if args.end_year is not None else settings.ingestion_end_year,
        territorial_codes=territorial_codes,
        dry_run=args.dry_run,
        validate_territorial_codes=not args.skip_territorial_validation,
        max_batches=args.max_batches,
    )


def run_ingest_sync(args: argparse.Namespace) -> int:
    registry = SOURCE_REGISTRY[args.source]
    settings = get_settings()
    init_engine(settings.database_url)
    catalog = None if args.skip_territorial_validation else DivipolaCatalog.from_file(
        settings.divipola_catalog_path,
    )
    session_gen = get_session()
    session = next(session_gen)
    try:
        use_case = SyncIngestHealthIndicatorsUseCase(
            source_client=_build_source_client(registry, catalog=catalog),
            repository=SqlAlchemyIngestionRepository(session),
            territorial_catalog=catalog,
        )
        result = use_case.execute(
            _build_sync_command(registry, args, settings),
            progress=lambda message: print(message, flush=True),
        )
    finally:
        session_gen.close()
        dispose_engine()

    rejected_codes = ",".join(result.rejected_territorial_codes) or "-"
    years = ",".join(str(year) for year in result.years_processed) or "-"
    print(
        "Sync ingestion completed: "
        f"run_id={result.run_id} "
        f"batches={result.batches_processed} "
        f"years={years} "
        f"records_upserted={result.records_upserted} "
        f"records_rejected={result.records_rejected} "
        f"rejected_codes={rejected_codes}",
    )
    return 0


def _parse_definition_ids(raw_ids: str | None) -> tuple[str, ...] | None:
    if not raw_ids:
        return None
    ids = tuple(item.strip() for item in raw_ids.split(",") if item.strip())
    return ids or None


def run_ingest_sync_municipal(args: argparse.Namespace) -> int:
    settings = get_settings()
    init_engine(settings.database_url)
    catalog = None if args.skip_territorial_validation else DivipolaCatalog.from_file(
        settings.divipola_catalog_path,
    )
    if catalog is None:
        msg = "Municipal sync requires DIVIPOLA catalog validation."
        raise ValueError(msg)

    session_gen = get_session()
    session = next(session_gen)
    try:
        fetcher = MunicipalDatasetFetcher(catalog)
        resolver = MunicipalDatasetResolver(fetcher)
        use_case = SyncMunicipalIndicatorsUseCase(
            resolver,
            SqlAlchemyIngestionRepository(session),
            territorial_catalog=catalog,
        )
        result = use_case.execute(
            default_municipal_sync_command(
                territorial_codes=_parse_territorial_codes(getattr(args, "territorial_codes", None)),
                definition_ids=_parse_definition_ids(getattr(args, "definition_ids", None)),
                batch_size=args.batch_size or settings.ingestion_batch_size,
                start_year=args.start_year,
                end_year=args.end_year if args.end_year is not None else settings.ingestion_end_year,
                dry_run=args.dry_run,
                validate_territorial_codes=not args.skip_territorial_validation,
                max_batches=args.max_batches,
            ),
            progress=lambda message: print(message, flush=True),
        )
    finally:
        session_gen.close()
        dispose_engine()

    rejected_codes = ",".join(result.rejected_territorial_codes) or "-"
    years = ",".join(str(year) for year in result.years_processed) or "-"
    print(
        "Municipal sync completed: "
        f"run_id={result.run_id} "
        f"batches={result.batches_processed} "
        f"years={years} "
        f"records_upserted={result.records_upserted} "
        f"records_rejected={result.records_rejected} "
        f"rejected_codes={rejected_codes}",
    )
    return 0


def run_ingest_sync_all(args: argparse.Namespace) -> int:
    exit_code = 0
    for source_key in SYNC_SOURCE_ORDER:
        print(f"\n=== Sync source: {source_key} ===", flush=True)
        source_args = argparse.Namespace(
            source=source_key,
            batch_size=args.batch_size,
            start_year=args.start_year,
            end_year=args.end_year,
            all_municipalities=args.all_municipalities,
            territorial_codes=getattr(args, "territorial_codes", None),
            max_batches=args.max_batches,
            dry_run=args.dry_run,
            skip_territorial_validation=args.skip_territorial_validation,
        )
        exit_code = max(exit_code, run_ingest_sync(source_args))
    return exit_code


def run_ingest(args: argparse.Namespace) -> int:
    registry = SOURCE_REGISTRY[args.source]
    years = _parse_years(args.years)
    settings = get_settings()
    init_engine(settings.database_url)
    catalog = None if args.skip_territorial_validation else DivipolaCatalog.from_file(
        settings.divipola_catalog_path,
    )
    session_gen = get_session()
    session = next(session_gen)
    try:
        use_case = IngestHealthIndicatorsUseCase(
            source_client=_build_source_client(registry, catalog=catalog),
            repository=SqlAlchemyIngestionRepository(session),
            territorial_catalog=catalog,
        )
        result = use_case.execute(
            IngestHealthIndicatorsCommand(
                source_id=registry["source_id"],
                definition_id=registry["definition_id"],
                source_indicator_key=registry["source_indicator_key"],
                year=None if years else args.year,
                years=years,
                limit=args.limit,
                dry_run=args.dry_run,
                validate_territorial_codes=not args.skip_territorial_validation,
            ),
        )
    finally:
        session_gen.close()
        dispose_engine()

    rejected_codes = ",".join(result.rejected_territorial_codes) or "-"
    print(
        "Ingestion completed: "
        f"run_id={result.run_id} "
        f"records_upserted={result.records_upserted} "
        f"records_rejected={result.records_rejected} "
        f"rejected_codes={rejected_codes}",
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest":
        return run_ingest(args)
    if args.command == "ingest-sync":
        return run_ingest_sync(args)
    if args.command == "ingest-sync-municipal":
        return run_ingest_sync_municipal(args)
    if args.command == "ingest-sync-all":
        return run_ingest_sync_all(args)

    parser.error(f"Unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

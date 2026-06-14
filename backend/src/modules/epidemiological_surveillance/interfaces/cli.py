"""CLI for epidemiological data ingestion."""

from __future__ import annotations

import argparse
import sys

from config.settings import get_settings
from infrastructure.persistence.database import dispose_engine, get_session, init_engine
from modules.epidemiological_surveillance.application.ingest_mortality_indicators import (
    IngestMortalityIndicatorsUseCase,
)
from modules.epidemiological_surveillance.application.normalization import (
    IngestMortalityIndicatorsCommand,
)
from modules.epidemiological_surveillance.infrastructure.persistence.sqlalchemy_ingestion_repository import (  # noqa: E501
    SqlAlchemyIngestionRepository,
)
from modules.epidemiological_surveillance.infrastructure.sources.datos_gov_co_client import (
    GENERAL_MORTALITY_INDICATOR,
    DatosGovCoMortalityClient,
)
from shared.divipola_catalog import DivipolaCatalog

SOURCE_DATOS_GOV_MORTALITY = "datos-gov-mortality-indicators"
DEFINITION_GENERAL_MORTALITY = "general-mortality-rate"

SOURCE_REGISTRY = {
    SOURCE_DATOS_GOV_MORTALITY: {
        "source_id": SOURCE_DATOS_GOV_MORTALITY,
        "definition_id": DEFINITION_GENERAL_MORTALITY,
        "source_indicator_key": GENERAL_MORTALITY_INDICATOR,
    },
}


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
    return parser


def _parse_years(raw_years: str | None) -> tuple[int, ...] | None:
    if not raw_years:
        return None
    years = tuple(int(value.strip()) for value in raw_years.split(",") if value.strip())
    if not years:
        msg = "At least one year must be provided when using --years."
        raise ValueError(msg)
    return years


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
        use_case = IngestMortalityIndicatorsUseCase(
            source_client=DatosGovCoMortalityClient(
                source_indicator_key=registry["source_indicator_key"],
            ),
            repository=SqlAlchemyIngestionRepository(session),
            territorial_catalog=catalog,
        )
        result = use_case.execute(
            IngestMortalityIndicatorsCommand(
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

    parser.error(f"Unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

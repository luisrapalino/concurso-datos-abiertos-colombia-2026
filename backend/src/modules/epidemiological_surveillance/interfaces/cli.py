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
    return parser


def run_ingest(args: argparse.Namespace) -> int:
    registry = SOURCE_REGISTRY[args.source]
    settings = get_settings()
    init_engine(settings.database_url)
    session_gen = get_session()
    session = next(session_gen)
    try:
        use_case = IngestMortalityIndicatorsUseCase(
            source_client=DatosGovCoMortalityClient(
                source_indicator_key=registry["source_indicator_key"],
            ),
            repository=SqlAlchemyIngestionRepository(session),
        )
        result = use_case.execute(
            IngestMortalityIndicatorsCommand(
                source_id=registry["source_id"],
                definition_id=registry["definition_id"],
                source_indicator_key=registry["source_indicator_key"],
                year=args.year,
                limit=args.limit,
                dry_run=args.dry_run,
            ),
        )
    finally:
        session_gen.close()
        dispose_engine()

    print(
        f"Ingestion completed: run_id={result.run_id} records_upserted={result.records_upserted}",
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

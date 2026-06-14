"""Scheduled ingestion worker for epidemiological surveillance sources."""

from __future__ import annotations

import argparse
import signal
import sys
import time
from collections.abc import Callable

from config.settings import Settings, get_settings
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
from modules.epidemiological_surveillance.interfaces.cli import SOURCE_REGISTRY
from shared.divipola_catalog import DivipolaCatalog

_shutdown_requested = False


def _handle_shutdown_signal(_signum: int, _frame: object | None) -> None:
    global _shutdown_requested
    _shutdown_requested = True


def parse_years(raw_years: str) -> tuple[int, ...]:
    years = tuple(int(value.strip()) for value in raw_years.split(",") if value.strip())
    if not years:
        msg = "At least one year must be provided for scheduled ingestion."
        raise ValueError(msg)
    return years


def build_ingestion_command(settings: Settings) -> IngestMortalityIndicatorsCommand:
    registry = SOURCE_REGISTRY["datos-gov-mortality-indicators"]
    years = parse_years(settings.ingestion_default_years)
    return IngestMortalityIndicatorsCommand(
        source_id=registry["source_id"],
        definition_id=registry["definition_id"],
        source_indicator_key=registry["source_indicator_key"],
        years=years,
        limit=settings.ingestion_default_limit,
        validate_territorial_codes=settings.ingestion_validate_territorial_codes,
    )


def run_ingestion_once(settings: Settings) -> None:
    catalog = DivipolaCatalog.from_file(settings.divipola_catalog_path)
    init_engine(settings.database_url)
    session_gen = get_session()
    session = next(session_gen)
    try:
        use_case = IngestMortalityIndicatorsUseCase(
            source_client=DatosGovCoMortalityClient(
                source_indicator_key=GENERAL_MORTALITY_INDICATOR,
            ),
            repository=SqlAlchemyIngestionRepository(session),
            territorial_catalog=catalog,
        )
        result = use_case.execute(build_ingestion_command(settings))
    finally:
        session_gen.close()
        dispose_engine()

    rejected_codes = ",".join(result.rejected_territorial_codes) or "-"
    print(
        "Scheduled ingestion completed: "
        f"run_id={result.run_id} "
        f"records_upserted={result.records_upserted} "
        f"records_rejected={result.records_rejected} "
        f"rejected_codes={rejected_codes}",
        flush=True,
    )


def run_scheduler_loop(
    settings: Settings,
    *,
    sleep_fn: Callable[[float], None] = time.sleep,
    run_once_fn: Callable[[Settings], None] = run_ingestion_once,
) -> int:
    interval_seconds = settings.ingestion_interval_hours * 3600
    print(
        "Starting ingestion scheduler: "
        f"interval_hours={settings.ingestion_interval_hours} "
        f"years={settings.ingestion_default_years} "
        f"limit={settings.ingestion_default_limit}",
        flush=True,
    )

    while not _shutdown_requested:
        run_once_fn(settings)
        if _shutdown_requested:
            break

        slept = 0.0
        while slept < interval_seconds and not _shutdown_requested:
            sleep_fn(min(60.0, interval_seconds - slept))
            slept += min(60.0, interval_seconds - slept)

    print("Ingestion scheduler stopped.", flush=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scheduled epidemiological ingestion worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single ingestion cycle and exit",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    signal.signal(signal.SIGTERM, _handle_shutdown_signal)
    signal.signal(signal.SIGINT, _handle_shutdown_signal)

    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_settings()

    if not settings.ingestion_schedule_enabled and not args.once:
        print("Ingestion scheduler disabled (INGESTION_SCHEDULE_ENABLED=false).", flush=True)
        return 0

    if args.once:
        run_ingestion_once(settings)
        return 0

    return run_scheduler_loop(settings)


if __name__ == "__main__":
    sys.exit(main())

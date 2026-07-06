"""Scheduled incremental sync worker for open data sources."""

from __future__ import annotations

import argparse
import signal
import sys
import time
from collections.abc import Callable

from config.settings import Settings, get_settings
from infrastructure.persistence.database import dispose_engine, get_session, init_engine
from modules.epidemiological_surveillance.application.municipal_dataset_resolver import (
    MunicipalDatasetResolver,
)
from modules.epidemiological_surveillance.application.sync_municipal_indicators import (
    SyncMunicipalIndicatorsUseCase,
    default_municipal_sync_command,
)
from modules.epidemiological_surveillance.infrastructure.persistence.sqlalchemy_ingestion_repository import (  # noqa: E501
    SqlAlchemyIngestionRepository,
)
from modules.epidemiological_surveillance.infrastructure.sources.municipal_dataset_fetcher import (
    MunicipalDatasetFetcher,
)
from shared.divipola_catalog import DivipolaCatalog

_shutdown_requested = False


def _handle_shutdown_signal(_signum: int, _frame: object | None) -> None:
    global _shutdown_requested
    _shutdown_requested = True


def run_sync_once(settings: Settings) -> None:
    catalog = DivipolaCatalog.from_file(settings.divipola_catalog_path)
    init_engine(settings.database_url)

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
                territorial_codes=None,
                definition_ids=None,
                batch_size=settings.ingestion_batch_size,
                start_year=None,
                end_year=settings.ingestion_end_year,
                dry_run=False,
                validate_territorial_codes=settings.ingestion_validate_territorial_codes,
                max_batches=None,
            ),
            progress=lambda message: print(message, flush=True),
        )
    finally:
        session_gen.close()

    print(
        "Scheduled municipal sync completed: "
        f"batches={result.batches_processed} "
        f"records_upserted={result.records_upserted} "
        f"records_rejected={result.records_rejected}",
        flush=True,
    )

    dispose_engine()


def run_scheduler_loop(
    settings: Settings,
    *,
    sleep_fn: Callable[[float], None] = time.sleep,
    run_once_fn: Callable[[Settings], None] = run_sync_once,
) -> int:
    interval_seconds = settings.ingestion_interval_hours * 3600
    print(
        "Starting municipal sync scheduler: "
        f"interval_hours={settings.ingestion_interval_hours} "
        f"batch_size={settings.ingestion_batch_size} "
        f"end_year={settings.ingestion_end_year}",
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

    print("Municipal sync scheduler stopped.", flush=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scheduled incremental open-data sync worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single sync cycle and exit",
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
        run_sync_once(settings)
        return 0

    return run_scheduler_loop(settings)


if __name__ == "__main__":
    sys.exit(main())

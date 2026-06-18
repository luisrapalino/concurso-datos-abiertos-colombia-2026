import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from api.main import create_app
from config.settings import get_settings
from infrastructure.persistence.database import dispose_engine, get_session, init_engine
from modules.epidemiological_surveillance.application.ingest_health_indicators import (
    IngestHealthIndicatorsUseCase,
)
from modules.epidemiological_surveillance.application.normalization import (
    IngestHealthIndicatorsCommand,
)
from modules.epidemiological_surveillance.infrastructure.persistence.sqlalchemy_ingestion_repository import (  # noqa: E501
    SqlAlchemyIngestionRepository,
)
from modules.epidemiological_surveillance.infrastructure.sources.client_adapters import (
    MortalityIndicatorsClientAdapter,
)
from modules.epidemiological_surveillance.infrastructure.sources.datos_gov_co_client import (
    DatosGovCoMortalityClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.sivigila_client import (
    SivigilaSurveillanceClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.vaccination_client import (
    VaccinationCoverageClient,
)
from modules.epidemiological_surveillance.interfaces.cli import SOURCE_REGISTRY
from shared.divipola_catalog import DivipolaCatalog


def _run_ingestion(
    session,
    catalog: DivipolaCatalog,
    source_key: str,
    *,
    year: int | None = None,
    limit: int = 5000,
) -> None:
    registry = SOURCE_REGISTRY[source_key]
    if registry["client_type"] == "mortality":
        client = MortalityIndicatorsClientAdapter(
            DatosGovCoMortalityClient(source_indicator_key=registry["source_indicator_key"]),
        )
    elif registry["client_type"] == "sivigila":
        client = SivigilaSurveillanceClient(event_code=registry["source_indicator_key"])
    elif registry["client_type"] == "vaccination":
        client = VaccinationCoverageClient(
            vaccine_name=registry["source_indicator_key"],
            territorial_catalog=catalog,
        )
    else:
        return

    use_case = IngestHealthIndicatorsUseCase(
        source_client=client,
        repository=SqlAlchemyIngestionRepository(session),
        territorial_catalog=catalog,
    )
    use_case.execute(
        IngestHealthIndicatorsCommand(
            source_id=registry["source_id"],
            definition_id=registry["definition_id"],
            source_indicator_key=registry["source_indicator_key"],
            year=year,
            limit=limit,
        ),
    )


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://epintel:epintel@localhost:5432/epintel",
    )


@pytest.fixture(scope="session")
def seeded_database(database_url: str) -> None:
    os.environ["DATABASE_URL"] = database_url
    get_settings.cache_clear()
    init_engine(database_url)

    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    alembic_cfg = Config(os.path.join(backend_root, "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    alembic_cfg.set_main_option("script_location", os.path.join(backend_root, "alembic"))
    command.upgrade(alembic_cfg, "head")

    session_gen = get_session()
    session = next(session_gen)
    catalog = DivipolaCatalog.from_file()
    try:
        _run_ingestion(
            session,
            catalog,
            "datos-gov-mortality-indicators",
            year=2020,
            limit=5000,
        )
        _run_ingestion(
            session,
            catalog,
            "datos-gov-sivigila-dengue",
            year=2020,
            limit=15000,
        )
        _run_ingestion(
            session,
            catalog,
            "datos-gov-vaccination-coverage",
            year=2020,
            limit=5000,
        )
        _run_ingestion(
            session,
            catalog,
            "datos-gov-health-access",
            year=2020,
            limit=5000,
        )
    finally:
        session_gen.close()
        dispose_engine()


@pytest.fixture(scope="session")
def client(database_url: str, seeded_database: None) -> TestClient:
    os.environ["DATABASE_URL"] = database_url
    get_settings.cache_clear()
    with TestClient(create_app()) as test_client:
        yield test_client

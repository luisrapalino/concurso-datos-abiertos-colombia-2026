import os

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
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
    DatosGovCoMortalityClient,
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
    session_gen = get_session()
    session = next(session_gen)
    try:
        use_case = IngestMortalityIndicatorsUseCase(
            source_client=DatosGovCoMortalityClient(),
            repository=SqlAlchemyIngestionRepository(session),
        )
        use_case.execute(
            IngestMortalityIndicatorsCommand(
                source_id="datos-gov-mortality-indicators",
                definition_id="general-mortality-rate",
                source_indicator_key="TASA DE MORTALIDAD GENERAL",
                year=2020,
                limit=5000,
            ),
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

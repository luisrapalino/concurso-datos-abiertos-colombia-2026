import os

import pytest
from fastapi.testclient import TestClient

from api.main import create_app


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://epintel:epintel@localhost:5432/epintel",
    )


@pytest.fixture(scope="session")
def client(database_url: str) -> TestClient:
    os.environ["DATABASE_URL"] = database_url
    with TestClient(create_app()) as test_client:
        yield test_client

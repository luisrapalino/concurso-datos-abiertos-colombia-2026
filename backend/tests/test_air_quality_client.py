from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from modules.epidemiological_surveillance.infrastructure.sources.air_quality_client import (
    AirQualityClient,
    open_data_municipality_code,
)


def test_open_data_municipality_code_normalizes_divipola() -> None:
    assert open_data_municipality_code("05001") == "5001"
    assert open_data_municipality_code("11001") == "11001"
    assert open_data_municipality_code("08001") == "8001"
    assert open_data_municipality_code("76001") == "76001"


def test_fetch_records_queries_by_municipality_and_aggregates_stations() -> None:
    http_client = MagicMock()
    http_client.get.return_value.json.return_value = [
        {
            "a_o": "2022",
            "promedio": "20.0",
            "nombre_del_municipio": "Medellin",
            "id_estacion": "1",
        },
        {
            "a_o": "2022",
            "promedio": "30.0",
            "nombre_del_municipio": "Medellin",
            "id_estacion": "2",
        },
    ]
    http_client.get.return_value.raise_for_status = MagicMock()

    client = AirQualityClient()
    records = client.fetch_records(
        year=2022,
        territorial_code="05001",
        http_client=http_client,
    )

    assert len(records) == 1
    assert records[0].territorial_code == "05001"
    assert records[0].period == "2022"
    assert records[0].value == Decimal("25.0000")

    params = http_client.get.call_args.kwargs["params"]
    assert "c_digo_del_municipio = '5001'" in params["$where"]
    assert "a_o = '2022'" in params["$where"]
    assert "PM2.5" in params["$where"]


def test_fetch_records_returns_empty_without_territorial_code_on_pagination() -> None:
    client = AirQualityClient()
    assert client.fetch_records(territorial_code="05001", offset=1) == []


@pytest.mark.integration
def test_fetch_records_live_for_medellin() -> None:
    client = AirQualityClient()
    records = client.fetch_records(year=2022, territorial_code="05001", limit=1000)
    assert records
    assert records[0].territorial_code == "05001"
    assert records[0].period == "2022"
    assert records[0].value > 0

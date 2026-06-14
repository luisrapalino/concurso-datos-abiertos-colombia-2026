import httpx
import pytest

from modules.epidemiological_surveillance.infrastructure.sources.datos_gov_co_client import (
    DatosGovCoMortalityClient,
)


def test_datos_gov_client_parses_sample_payload() -> None:
    sample = [
        {
            "coddepartamento": "05",
            "departamento": "Antioquia",
            "codmunicipio": "05001",
            "municipio": "Medellín",
            "indicador": "TASA DE MORTALIDAD GENERAL",
            "a_o": "2023",
            "valor_indicador": "6.123",
        }
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("indicador") == "TASA DE MORTALIDAD GENERAL"
        return httpx.Response(200, json=sample)

    client = DatosGovCoMortalityClient(base_url="https://example.test/resource.json")
    http_client = httpx.Client(transport=httpx.MockTransport(handler))

    records = client.fetch_general_mortality_records(
        year=2023,
        limit=1,
        http_client=http_client,
    )

    assert len(records) == 1
    assert records[0].territorial_code == "05001"
    assert records[0].year == 2023
    assert float(records[0].value) == pytest.approx(6.123)

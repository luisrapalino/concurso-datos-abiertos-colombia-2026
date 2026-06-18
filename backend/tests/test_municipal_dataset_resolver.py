from decimal import Decimal
from unittest.mock import MagicMock

from modules.epidemiological_surveillance.application.municipal_dataset_resolver import (
    MunicipalDatasetResolver,
)
from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from modules.epidemiological_surveillance.infrastructure.sources.municipal_dataset_fetcher import (
    MunicipalDatasetFetcher,
)
from shared.municipal_dataset_catalog import (
    DEFINITION_PM25,
    list_bindings_for_definition,
)


class _FakeFetcher:
    def __init__(self, responses: dict[tuple[str, str, int | None], list[RawHealthIndicatorRecord]]) -> None:
        self._responses = responses

    def fetch(self, binding, *, territorial_code, year, limit, offset):  # noqa: ANN001
        return self._responses.get(
            (binding.binding_id, territorial_code, year),
            [],
        )


def test_pm25_bindings_include_annual_and_sisaire_fallback() -> None:
    bindings = list_bindings_for_definition(DEFINITION_PM25)
    assert len(bindings) == 2
    assert bindings[0].binding_id == "pm25-annual-municipal"
    assert bindings[1].binding_id == "pm25-sisaire-daily"


def test_resolver_uses_first_binding_with_data() -> None:
    record = RawHealthIndicatorRecord(
        territorial_code="05001",
        territory_name="Medellín",
        source_indicator_key="pm25",
        period="2022",
        value=Decimal("20"),
    )
    fetcher = _FakeFetcher(
        {
            ("pm25-annual-municipal", "05001", 2022): [record],
            ("pm25-sisaire-daily", "05001", 2022): [record],
        },
    )
    resolver = MunicipalDatasetResolver(fetcher)  # type: ignore[arg-type]

    resolution = resolver.resolve_page(
        definition_id=DEFINITION_PM25,
        territorial_code="05001",
        year=2022,
        limit=100,
        offset=0,
    )

    assert resolution is not None
    assert resolution.binding.binding_id == "pm25-annual-municipal"
    assert len(resolution.records) == 1


def test_resolver_falls_back_when_primary_has_no_data() -> None:
    record = RawHealthIndicatorRecord(
        territorial_code="05001",
        territory_name="Medellín",
        source_indicator_key="pm25",
        period="2022",
        value=Decimal("12"),
    )
    fetcher = _FakeFetcher(
        {
            ("pm25-annual-municipal", "05001", 2022): [],
            ("pm25-sisaire-daily", "05001", 2022): [record],
        },
    )
    resolver = MunicipalDatasetResolver(fetcher)  # type: ignore[arg-type]

    resolution = resolver.resolve_page(
        definition_id=DEFINITION_PM25,
        territorial_code="05001",
        year=2022,
        limit=100,
        offset=0,
    )

    assert resolution is not None
    assert resolution.binding.binding_id == "pm25-sisaire-daily"
    assert resolution.records[0].value == Decimal("12")


def test_municipal_dataset_fetcher_builds_mortality_client() -> None:
    catalog = MagicMock()
    catalog.municipality_name.return_value = "Medellín"
    fetcher = MunicipalDatasetFetcher(catalog)
    binding = list_bindings_for_definition("general-mortality-rate")[0]
    client = fetcher._build_client(binding.client_type, binding.source_indicator_key)
    assert hasattr(client, "fetch_records")

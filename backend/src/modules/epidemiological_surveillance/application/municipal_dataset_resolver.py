from __future__ import annotations

from dataclasses import dataclass

import httpx

from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from modules.epidemiological_surveillance.infrastructure.sources.municipal_dataset_fetcher import (
    MunicipalDatasetFetcher,
)
from shared.municipal_dataset_catalog import (
    MunicipalDatasetBinding,
    list_bindings_for_definition,
)


@dataclass(frozen=True, slots=True)
class MunicipalDatasetResolution:
    binding: MunicipalDatasetBinding
    records: list[RawHealthIndicatorRecord]
    tried_binding_ids: tuple[str, ...]


class MunicipalDatasetResolver:
    """Selects the best available open dataset for a municipality-variable pair."""

    def __init__(self, fetcher: MunicipalDatasetFetcher) -> None:
        self._fetcher = fetcher

    def resolve_page(
        self,
        *,
        definition_id: str,
        territorial_code: str,
        year: int | None,
        limit: int,
        offset: int,
        locked_binding: MunicipalDatasetBinding | None = None,
    ) -> MunicipalDatasetResolution | None:
        candidates = (
            (locked_binding,)
            if locked_binding is not None
            else list_bindings_for_definition(definition_id)
        )
        if not candidates or candidates[0] is None:
            return None

        tried: list[str] = []
        for binding in candidates:
            if binding is None:
                continue
            tried.append(binding.binding_id)
            try:
                records = self._fetcher.fetch(
                    binding,
                    territorial_code=territorial_code,
                    year=year,
                    limit=limit,
                    offset=offset,
                )
            except (httpx.HTTPError, httpx.RequestError, ValueError):
                if locked_binding is not None:
                    return MunicipalDatasetResolution(
                        binding=binding,
                        records=[],
                        tried_binding_ids=tuple(tried),
                    )
                continue
            if records or locked_binding is not None:
                return MunicipalDatasetResolution(
                    binding=binding,
                    records=records,
                    tried_binding_ids=tuple(tried),
                )
        return None

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.application.municipal_variable_dataset_dto import (
    MunicipalVariableDatasetDto,
)
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorObservationRow,
)
from shared.divipola_catalog import DivipolaCatalog
from shared.featured_municipalities import FEATURED_MUNICIPALITY_CODES
from shared.municipal_dataset_catalog import (
    COMPETITION_DEFINITION_IDS,
    list_bindings_for_definition,
    variable_display_name,
)


class ListMunicipalVariableDatasetsUseCase:
    """Shows which open dataset serves each municipality-variable pair in the pilot."""

    def __init__(self, session: Session, *, catalog: DivipolaCatalog) -> None:
        self._session = session
        self._catalog = catalog

    def execute(self) -> list[MunicipalVariableDatasetDto]:
        rows: list[MunicipalVariableDatasetDto] = []

        for territorial_code in FEATURED_MUNICIPALITY_CODES:
            municipality_name = self._catalog.municipality_name(territorial_code) or territorial_code
            for definition_id in COMPETITION_DEFINITION_IDS:
                bindings = list_bindings_for_definition(definition_id)
                if not bindings:
                    continue

                stats = self._session.execute(
                    select(
                        func.count(HealthIndicatorObservationRow.id),
                        func.max(HealthIndicatorObservationRow.period),
                    ).where(
                        HealthIndicatorObservationRow.definition_id == definition_id,
                        HealthIndicatorObservationRow.territorial_code == territorial_code,
                    ),
                ).one()
                records_ingested = int(stats[0] or 0)
                latest_period = stats[1]

                preferred = bindings[0]
                resolution_note = preferred.selection_note
                if records_ingested == 0 and len(bindings) > 1:
                    resolution_note = (
                        f"Sin datos en {preferred.binding_id}; "
                        f"respaldo disponible: {bindings[1].binding_id}"
                    )

                rows.append(
                    MunicipalVariableDatasetDto(
                        territorial_code=territorial_code,
                        municipality_name=municipality_name.title(),
                        definition_id=definition_id,
                        variable_name=variable_display_name(definition_id),
                        active_binding_id=preferred.binding_id,
                        source_id=preferred.source_id,
                        api_url=preferred.api_url,
                        portal_url=preferred.portal_url,
                        provider=preferred.provider,
                        granularity=preferred.granularity,
                        selection_note=preferred.selection_note,
                        fallback_binding_ids=[
                            binding.binding_id for binding in bindings[1:]
                        ],
                        records_ingested=records_ingested,
                        latest_period=latest_period,
                        resolution_note=resolution_note,
                    ),
                )

        rows.sort(key=lambda item: (item.municipality_name, item.variable_name))
        return rows

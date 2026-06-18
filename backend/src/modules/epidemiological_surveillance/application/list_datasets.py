from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from modules.epidemiological_surveillance.application.dataset_dto import DatasetReadDto
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorDefinitionRow,
    HealthIndicatorObservationRow,
    IngestionRunRow,
    IngestionRunStatus,
)
from shared.open_data_catalog import resolve_open_data_meta


class ListDatasetsUseCase:
    """Catalog of ingested open-data definitions with live counts from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def execute(self) -> list[DatasetReadDto]:
        definitions = self._session.scalars(
            select(HealthIndicatorDefinitionRow)
            .options(joinedload(HealthIndicatorDefinitionRow.source))
            .order_by(
                HealthIndicatorDefinitionRow.source_id,
                HealthIndicatorDefinitionRow.id,
            ),
        ).unique().all()

        datasets: list[DatasetReadDto] = []
        for definition in definitions:
            stats = self._session.execute(
                select(
                    func.count(HealthIndicatorObservationRow.id),
                    func.count(func.distinct(HealthIndicatorObservationRow.territorial_code)),
                    func.max(HealthIndicatorObservationRow.period),
                ).where(
                    HealthIndicatorObservationRow.definition_id == definition.id,
                ),
            ).one()

            records_ingested = int(stats[0] or 0)
            municipalities_count = int(stats[1] or 0)
            latest_period = stats[2]

            latest_run = self._session.scalars(
                select(IngestionRunRow)
                .where(
                    IngestionRunRow.source_id == definition.source_id,
                    IngestionRunRow.status == IngestionRunStatus.SUCCEEDED.value,
                )
                .order_by(IngestionRunRow.finished_at.desc())
                .limit(1),
            ).first()

            meta = resolve_open_data_meta(definition.source_id)
            source = definition.source
            fallback_url = source.base_url if source is not None else ""

            datasets.append(
                DatasetReadDto(
                    definition_id=definition.id,
                    name=definition.name,
                    source_id=definition.source_id,
                    source_name=source.name if source is not None else definition.source_id,
                    provider=(
                        meta.provider
                        if meta is not None
                        else (source.provider if source is not None else "datos.gov.co")
                    ),
                    portal_url=meta.portal_url if meta is not None else fallback_url,
                    api_url=meta.api_url if meta is not None else fallback_url,
                    measurement_unit=definition.measurement_unit,
                    granularity=source.granularity if source is not None else "unknown",
                    records_ingested=records_ingested,
                    municipalities_count=municipalities_count,
                    latest_period=latest_period,
                    last_ingestion_at=(
                        latest_run.finished_at if latest_run is not None else None
                    ),
                ),
            )

        datasets.sort(key=lambda item: item.records_ingested, reverse=True)
        return datasets

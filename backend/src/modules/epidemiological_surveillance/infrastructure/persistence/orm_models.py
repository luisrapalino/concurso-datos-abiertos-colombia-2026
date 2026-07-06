from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.persistence.base import Base


class IngestionRunStatus(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class DataSourceRow(Base):
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    license: Mapped[str | None] = mapped_column(String(255), nullable=True)
    base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    granularity: Mapped[str] = mapped_column(String(64), nullable=False)
    update_frequency: Mapped[str | None] = mapped_column(String(128), nullable=True)

    definitions: Mapped[list[HealthIndicatorDefinitionRow]] = relationship(back_populates="source")
    ingestion_runs: Mapped[list[IngestionRunRow]] = relationship(back_populates="source")


class IngestionRunRow(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("data_sources.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    records_upserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    batches_processed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    years_processed: Mapped[str | None] = mapped_column(String(255), nullable=True)
    territorial_codes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sync_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bindings_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped[DataSourceRow] = relationship(back_populates="ingestion_runs")
    observations: Mapped[list[HealthIndicatorObservationRow]] = relationship(
        back_populates="ingestion_run",
    )


class HealthIndicatorDefinitionRow(Base):
    __tablename__ = "health_indicator_definitions"
    __table_args__ = (
        UniqueConstraint("source_id", "source_indicator_key", name="uq_definition_source_key"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    measurement_unit: Mapped[str] = mapped_column(String(64), nullable=False)
    source_indicator_key: Mapped[str] = mapped_column(String(255), nullable=False)
    source_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("data_sources.id"),
        nullable=False,
    )

    source: Mapped[DataSourceRow] = relationship(back_populates="definitions")
    observations: Mapped[list[HealthIndicatorObservationRow]] = relationship(
        back_populates="definition",
    )


class HealthIndicatorObservationRow(Base):
    __tablename__ = "health_indicator_observations"
    __table_args__ = (
        UniqueConstraint(
            "definition_id",
            "territorial_code",
            "period",
            name="uq_health_indicator_observations_definition_territory_period",
        ),
    )

    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    definition_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("health_indicator_definitions.id"),
        nullable=False,
    )
    territorial_code: Mapped[str] = mapped_column(String(32), nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    ingestion_run_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("ingestion_runs.id"),
        nullable=False,
    )

    definition: Mapped[HealthIndicatorDefinitionRow] = relationship(back_populates="observations")
    ingestion_run: Mapped[IngestionRunRow] = relationship(back_populates="observations")


def utc_now() -> datetime:
    return datetime.now(tz=UTC)

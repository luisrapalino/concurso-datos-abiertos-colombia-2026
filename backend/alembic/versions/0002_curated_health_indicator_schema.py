"""Curated epidemiological schema and retirement of placeholder health_indicators."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCE_ID = "datos-gov-mortality-indicators"
DEFINITION_ID = "general-mortality-rate"


def upgrade() -> None:
    op.drop_table("health_indicators")

    op.create_table(
        "data_sources",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=255), nullable=False),
        sa.Column("license", sa.String(length=255), nullable=True),
        sa.Column("base_url", sa.String(length=512), nullable=False),
        sa.Column("granularity", sa.String(length=64), nullable=False),
        sa.Column("update_frequency", sa.String(length=128), nullable=True),
    )

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("source_id", sa.String(length=64), sa.ForeignKey("data_sources.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_upserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_ingestion_runs_source_id", "ingestion_runs", ["source_id"])

    op.create_table(
        "health_indicator_definitions",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("measurement_unit", sa.String(length=64), nullable=False),
        sa.Column("source_indicator_key", sa.String(length=255), nullable=False),
        sa.Column("source_id", sa.String(length=64), sa.ForeignKey("data_sources.id"), nullable=False),
    )
    op.create_index(
        "ix_health_indicator_definitions_source_key",
        "health_indicator_definitions",
        ["source_id", "source_indicator_key"],
        unique=True,
    )

    op.create_table(
        "health_indicator_observations",
        sa.Column("id", sa.String(length=96), primary_key=True, nullable=False),
        sa.Column(
            "definition_id",
            sa.String(length=64),
            sa.ForeignKey("health_indicator_definitions.id"),
            nullable=False,
        ),
        sa.Column("territorial_code", sa.String(length=32), nullable=False),
        sa.Column("period", sa.String(length=7), nullable=False),
        sa.Column("value", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "ingestion_run_id",
            sa.String(length=64),
            sa.ForeignKey("ingestion_runs.id"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "definition_id",
            "territorial_code",
            "period",
            name="uq_health_indicator_observations_definition_territory_period",
        ),
    )
    op.create_index(
        "ix_health_indicator_observations_territorial_code",
        "health_indicator_observations",
        ["territorial_code"],
    )
    op.create_index(
        "ix_health_indicator_observations_period",
        "health_indicator_observations",
        ["period"],
    )

    data_sources = sa.table(
        "data_sources",
        sa.column("id", sa.String()),
        sa.column("name", sa.String()),
        sa.column("provider", sa.String()),
        sa.column("license", sa.String()),
        sa.column("base_url", sa.String()),
        sa.column("granularity", sa.String()),
        sa.column("update_frequency", sa.String()),
    )
    op.bulk_insert(
        data_sources,
        [
            {
                "id": SOURCE_ID,
                "name": "Indicadores mortalidad y morbilidad (departamento, municipio, año)",
                "provider": "INS / Datos Abiertos Colombia",
                "license": "Datos abiertos Colombia",
                "base_url": "https://www.datos.gov.co/resource/4e4i-ua65.json",
                "granularity": "municipality",
                "update_frequency": "annual (portal publication)",
            }
        ],
    )

    definitions = sa.table(
        "health_indicator_definitions",
        sa.column("id", sa.String()),
        sa.column("name", sa.String()),
        sa.column("measurement_unit", sa.String()),
        sa.column("source_indicator_key", sa.String()),
        sa.column("source_id", sa.String()),
    )
    op.bulk_insert(
        definitions,
        [
            {
                "id": DEFINITION_ID,
                "name": "Tasa de mortalidad general",
                "measurement_unit": "per 1000",
                "source_indicator_key": "TASA DE MORTALIDAD GENERAL",
                "source_id": SOURCE_ID,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("health_indicator_observations")
    op.drop_table("health_indicator_definitions")
    op.drop_index("ix_ingestion_runs_source_id", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
    op.drop_table("data_sources")

    op.create_table(
        "health_indicators",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("territorial_code", sa.String(length=32), nullable=True),
        sa.Column("measurement_unit", sa.String(length=64), nullable=True),
    )
    health_indicators = sa.table(
        "health_indicators",
        sa.column("id", sa.String()),
        sa.column("name", sa.String()),
        sa.column("territorial_code", sa.String()),
        sa.column("measurement_unit", sa.String()),
    )
    op.bulk_insert(
        health_indicators,
        [
            {
                "id": "stub-mortality-rate",
                "name": "Crude mortality rate (placeholder)",
                "territorial_code": None,
                "measurement_unit": "per 100k",
            }
        ],
    )

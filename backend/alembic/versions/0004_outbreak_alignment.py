"""Outbreak prediction alignment: new data sources, definitions and predictions table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCE_SIVIGILA = "datos-gov-sivigila"
SOURCE_VACCINATION = "datos-gov-vaccination-coverage"
SOURCE_AIR_QUALITY = "datos-gov-air-quality"
SOURCE_HEALTH_ACCESS = "datos-gov-mortality-indicators"

DEFINITION_DENGUE = "dengue-weekly-cases"
DEFINITION_VACCINATION = "dpta-penta-vaccination-coverage"
DEFINITION_PM25 = "pm25-annual-mean"
DEFINITION_HEALTH_ACCESS = "institutional-births-coverage"


def upgrade() -> None:
    op.alter_column(
        "health_indicator_observations",
        "period",
        existing_type=sa.String(length=7),
        type_=sa.String(length=16),
        existing_nullable=False,
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
                "id": SOURCE_SIVIGILA,
                "name": "Datos de Vigilancia en Salud Pública de Colombia (SIVIGILA)",
                "provider": "INS / Datos Abiertos Colombia",
                "license": "Datos abiertos Colombia",
                "base_url": "https://www.datos.gov.co/resource/4hyg-wa9d.json",
                "granularity": "municipality-weekly",
                "update_frequency": "weekly (portal publication)",
            },
            {
                "id": SOURCE_VACCINATION,
                "name": "Coberturas administrativas de vacunación por departamento",
                "provider": "MinSalud / Datos Abiertos Colombia",
                "license": "Datos abiertos Colombia",
                "base_url": "https://www.datos.gov.co/resource/6i25-2hdt.json",
                "granularity": "department-annual",
                "update_frequency": "annual (portal publication)",
            },
            {
                "id": SOURCE_AIR_QUALITY,
                "name": "Sistema de Información sobre Calidad del Aire PM10 y PM2.5 (SISAIRE)",
                "provider": "IDEAM / Datos Abiertos Colombia",
                "license": "Datos abiertos Colombia",
                "base_url": "https://www.datos.gov.co/resource/yspz-pxxn.json",
                "granularity": "station-daily",
                "update_frequency": "daily (portal publication)",
            },
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
                "id": DEFINITION_DENGUE,
                "name": "Casos semanales de dengue (SIVIGILA)",
                "measurement_unit": "cases",
                "source_indicator_key": "210",
                "source_id": SOURCE_SIVIGILA,
            },
            {
                "id": DEFINITION_VACCINATION,
                "name": "Cobertura DPT-HepB-Hib pentavalente",
                "measurement_unit": "percent",
                "source_indicator_key": "DPT - Hepatitis B - Hib (Pentavalente)",
                "source_id": SOURCE_VACCINATION,
            },
            {
                "id": DEFINITION_PM25,
                "name": "PM2.5 promedio anual",
                "measurement_unit": "ug/m3",
                "source_indicator_key": "pm25",
                "source_id": SOURCE_AIR_QUALITY,
            },
            {
                "id": DEFINITION_HEALTH_ACCESS,
                "name": "Porcentaje de partos institucionales (proxy acceso)",
                "measurement_unit": "percent",
                "source_indicator_key": "PORCENTAJE DE PARTOS INSTITUCIONALES",
                "source_id": SOURCE_HEALTH_ACCESS,
            },
        ],
    )

    op.create_table(
        "outbreak_predictions",
        sa.Column("id", sa.String(length=160), primary_key=True, nullable=False),
        sa.Column("territorial_code", sa.String(length=32), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("event_code", sa.String(length=16), nullable=False),
        sa.Column("event_name", sa.String(length=128), nullable=False),
        sa.Column("outbreak_probability", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("classification", sa.String(length=16), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("observed_cases", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("baseline_cases", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("assumptions", JSONB, nullable=False),
        sa.Column("drivers", JSONB, nullable=False),
        sa.Column("feature_contributions", JSONB, nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "territorial_code",
            "period",
            "event_code",
            "model_version",
            name="uq_outbreak_predictions_territory_period_event_model",
        ),
    )
    op.create_index(
        "ix_outbreak_predictions_territorial_code_period",
        "outbreak_predictions",
        ["territorial_code", "period"],
    )


def downgrade() -> None:
    op.drop_index("ix_outbreak_predictions_territorial_code_period")
    op.drop_table("outbreak_predictions")

    op.execute(
        sa.text(
            "DELETE FROM health_indicator_definitions WHERE id IN "
            "('dengue-weekly-cases', 'dpta-penta-vaccination-coverage', "
            "'pm25-annual-mean', 'institutional-births-coverage')"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM data_sources WHERE id IN "
            "('datos-gov-sivigila', 'datos-gov-vaccination-coverage', "
            "'datos-gov-air-quality')"
        )
    )

    op.alter_column(
        "health_indicator_observations",
        "period",
        existing_type=sa.String(length=16),
        type_=sa.String(length=7),
        existing_nullable=False,
    )

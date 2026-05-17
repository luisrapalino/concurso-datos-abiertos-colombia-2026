"""Create health_indicators table and seed placeholder row."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.drop_table("health_indicators")

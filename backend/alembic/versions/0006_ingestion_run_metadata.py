"""Extend ingestion_runs with sync metadata for traceability."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingestion_runs",
        sa.Column("records_rejected", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column("batches_processed", sa.Integer(), nullable=True),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column("years_processed", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column("territorial_codes", sa.Text(), nullable=True),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column("sync_mode", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "ingestion_runs",
        sa.Column("bindings_used", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ingestion_runs", "bindings_used")
    op.drop_column("ingestion_runs", "sync_mode")
    op.drop_column("ingestion_runs", "territorial_codes")
    op.drop_column("ingestion_runs", "years_processed")
    op.drop_column("ingestion_runs", "batches_processed")
    op.drop_column("ingestion_runs", "records_rejected")

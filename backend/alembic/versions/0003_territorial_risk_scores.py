"""Persist computed territorial risk scores."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "territorial_risk_scores",
        sa.Column("id", sa.String(length=128), primary_key=True, nullable=False),
        sa.Column("territorial_code", sa.String(length=32), nullable=False),
        sa.Column("period", sa.String(length=7), nullable=False),
        sa.Column("definition_id", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("classification", sa.String(length=16), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("observed_value", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("baseline_value", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("assumptions", JSONB, nullable=False),
        sa.Column("drivers", JSONB, nullable=False),
        sa.Column("feature_contributions", JSONB, nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "territorial_code",
            "period",
            "definition_id",
            "model_version",
            name="uq_territorial_risk_scores_territory_period_definition_model",
        ),
    )
    op.create_index(
        "ix_territorial_risk_scores_territorial_code_period",
        "territorial_risk_scores",
        ["territorial_code", "period"],
    )


def downgrade() -> None:
    op.drop_index("ix_territorial_risk_scores_territorial_code_period")
    op.drop_table("territorial_risk_scores")

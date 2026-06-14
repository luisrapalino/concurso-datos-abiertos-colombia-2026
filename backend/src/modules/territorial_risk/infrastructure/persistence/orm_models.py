from datetime import datetime

from sqlalchemy import DateTime, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.persistence.base import Base


class TerritorialRiskScoreRow(Base):
    __tablename__ = "territorial_risk_scores"
    __table_args__ = (
        UniqueConstraint(
            "territorial_code",
            "period",
            "definition_id",
            "model_version",
            name="uq_territorial_risk_scores_territory_period_definition_model",
        ),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    territorial_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    definition_id: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    classification: Mapped[str] = mapped_column(String(16), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_value: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    baseline_value: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    assumptions: Mapped[list] = mapped_column(JSONB, nullable=False)
    drivers: Mapped[list] = mapped_column(JSONB, nullable=False)
    feature_contributions: Mapped[list] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

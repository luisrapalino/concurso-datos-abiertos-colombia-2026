from datetime import datetime

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infrastructure.persistence.base import Base


class OutbreakPredictionRow(Base):
    __tablename__ = "outbreak_predictions"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    territorial_code: Mapped[str] = mapped_column(String(32), nullable=False)
    period: Mapped[str] = mapped_column(String(16), nullable=False)
    event_code: Mapped[str] = mapped_column(String(16), nullable=False)
    event_name: Mapped[str] = mapped_column(String(128), nullable=False)
    outbreak_probability: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    classification: Mapped[str] = mapped_column(String(16), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_cases: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    baseline_cases: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    assumptions: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    drivers: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    feature_contributions: Mapped[list[dict[str, object]]] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

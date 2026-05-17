from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.persistence.base import Base


class HealthIndicatorRow(Base):
    __tablename__ = "health_indicators"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    territorial_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    measurement_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)

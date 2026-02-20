import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ClimateData(Base):
    __tablename__ = "climate_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    embedding = mapped_column(Vector(384), nullable=True)

    country = relationship("Country", back_populates="climate_data")

    __table_args__ = (
        Index("ix_climate_data_country_date", "country_id", "date"),
        Index("ix_climate_data_metric_type", "metric_type"),
    )

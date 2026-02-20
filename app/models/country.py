from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    iso_code: Mapped[str] = mapped_column(String(2), unique=True, index=True, nullable=False)
    iso3_code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    capital_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    population: Mapped[int | None] = mapped_column(nullable=True)

    climate_data = relationship("ClimateData", back_populates="country", lazy="select")

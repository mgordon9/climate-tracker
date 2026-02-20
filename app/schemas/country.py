import datetime

from pydantic import BaseModel


class ClimateDataPoint(BaseModel):
    id: int
    date: datetime.date
    metric_type: str
    value: float
    unit: str
    source: str | None = None

    model_config = {"from_attributes": True}


class CountryList(BaseModel):
    id: int
    name: str
    iso_code: str
    iso3_code: str | None = None
    region: str | None = None
    capital_city: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = {"from_attributes": True}


class CountryDetail(CountryList):
    population: int | None = None
    climate_data: list[ClimateDataPoint] = []

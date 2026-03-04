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


class TimeSeriesPoint(BaseModel):
    year: int
    value: float


class TimeSeries(BaseModel):
    country_id: int
    country_name: str
    iso_code: str
    metric: str
    unit: str
    data: list[TimeSeriesPoint]


class GlobeCountry(BaseModel):
    id: int
    name: str
    iso_code: str
    iso3_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    latest_temp_change: float | None = None

    model_config = {"from_attributes": True}

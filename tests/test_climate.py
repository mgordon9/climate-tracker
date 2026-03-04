import datetime

import pytest

from app.models.climate_data import ClimateData
from app.models.country import Country


@pytest.fixture
def sample_climate_data(db_session, sample_country):
    """3 temperature records (2020/2021/2022) + 1 CO2 record for sample_country."""
    records = [
        ClimateData(
            country_id=sample_country.id,
            date=datetime.date(2020, 1, 1),
            metric_type="temperature_change",
            value=0.5,
            unit="°C",
        ),
        ClimateData(
            country_id=sample_country.id,
            date=datetime.date(2021, 1, 1),
            metric_type="temperature_change",
            value=0.7,
            unit="°C",
        ),
        ClimateData(
            country_id=sample_country.id,
            date=datetime.date(2022, 1, 1),
            metric_type="temperature_change",
            value=0.9,
            unit="°C",
        ),
        ClimateData(
            country_id=sample_country.id,
            date=datetime.date(2020, 1, 1),
            metric_type="co2_emissions",
            value=100.0,
            unit="Mt",
        ),
    ]
    for r in records:
        db_session.add(r)
    db_session.flush()
    return records


def test_get_climate_returns_data(client, sample_country, sample_climate_data):
    res = client.get(f"/api/countries/{sample_country.id}/climate?metric=temperature_change")
    assert res.status_code == 200
    data = res.json()
    assert data["country_id"] == sample_country.id
    assert data["metric"] == "temperature_change"
    years = [p["year"] for p in data["data"]]
    assert 2020 in years
    assert 2021 in years
    assert 2022 in years


def test_get_climate_metric_filter(client, sample_country, sample_climate_data):
    res = client.get(f"/api/countries/{sample_country.id}/climate?metric=co2_emissions")
    assert res.status_code == 200
    assert len(res.json()["data"]) == 1

    res = client.get(f"/api/countries/{sample_country.id}/climate?metric=temperature_change")
    assert res.status_code == 200
    assert len(res.json()["data"]) == 3


def test_get_climate_year_range(client, sample_country, sample_climate_data):
    res = client.get(
        f"/api/countries/{sample_country.id}/climate?metric=temperature_change&start_year=2021"
    )
    assert res.status_code == 200
    assert len(res.json()["data"]) == 2


def test_get_climate_country_not_found(client):
    res = client.get("/api/countries/99999/climate?metric=temperature_change")
    assert res.status_code == 404


def test_compare_two_countries(db_session, client, sample_country, sample_climate_data):
    country2 = Country(
        name="Otherland",
        iso_code="OL",
        iso3_code="OTL",
        region="Other Region",
        latitude=5.0,
        longitude=10.0,
    )
    db_session.add(country2)
    db_session.flush()
    db_session.add(
        ClimateData(
            country_id=country2.id,
            date=datetime.date(2020, 1, 1),
            metric_type="temperature_change",
            value=1.1,
            unit="°C",
        )
    )
    db_session.flush()

    res = client.get(
        f"/api/compare?country_ids={sample_country.id}&country_ids={country2.id}"
        "&metric=temperature_change"
    )
    assert res.status_code == 200
    result = res.json()
    assert len(result) == 2
    names = {r["country_name"] for r in result}
    assert "Testland" in names
    assert "Otherland" in names


def test_compare_skips_missing_country(client, sample_country, sample_climate_data):
    res = client.get(
        f"/api/compare?country_ids={sample_country.id}&country_ids=99999"
        "&metric=temperature_change"
    )
    assert res.status_code == 200
    result = res.json()
    assert len(result) == 1
    assert result[0]["country_name"] == "Testland"

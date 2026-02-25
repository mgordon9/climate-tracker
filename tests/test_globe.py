import datetime

import pytest

from app.models.climate_data import ClimateData
from app.models.country import Country


@pytest.fixture
def two_countries_with_temp(db_session):
    c1 = Country(name="Bigland", iso_code="BL", iso3_code="BGL", latitude=10.0, longitude=20.0)
    c2 = Country(name="Smalland", iso_code="SM", iso3_code="SML", latitude=-5.0, longitude=30.0)
    db_session.add_all([c1, c2])
    db_session.flush()

    # c1 has two readings — endpoint should return the most recent
    db_session.add_all([
        ClimateData(country_id=c1.id, date=datetime.date(2019, 1, 1),
                    metric_type="temperature_change", value=0.10, unit="°C"),
        ClimateData(country_id=c1.id, date=datetime.date(2021, 1, 1),
                    metric_type="temperature_change", value=0.25, unit="°C"),
    ])
    # c2 has no temperature_change data
    db_session.flush()
    return c1, c2


def test_globe_returns_all_countries(client, two_countries_with_temp):
    response = client.get("/api/globe")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert "Bigland" in names
    assert "Smalland" in names


def test_globe_returns_latest_temp_change(client, two_countries_with_temp):
    response = client.get("/api/globe")
    data = {c["name"]: c for c in response.json()}
    assert data["Bigland"]["latest_temp_change"] == pytest.approx(0.25)


def test_globe_null_for_missing_temp_change(client, two_countries_with_temp):
    response = client.get("/api/globe")
    data = {c["name"]: c for c in response.json()}
    assert data["Smalland"]["latest_temp_change"] is None


def test_globe_empty_db(client):
    response = client.get("/api/globe")
    assert response.status_code == 200
    assert response.json() == []


def test_globe_schema_fields(client, two_countries_with_temp):
    response = client.get("/api/globe")
    country = next(c for c in response.json() if c["name"] == "Bigland")
    assert "id" in country
    assert "name" in country
    assert "iso_code" in country
    assert "iso3_code" in country
    assert "latitude" in country
    assert "longitude" in country
    assert "latest_temp_change" in country

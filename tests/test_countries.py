def test_list_countries_empty(client):
    response = client.get("/api/countries")
    assert response.status_code == 200
    assert response.json() == []


def test_list_countries_with_data(client, sample_country):
    response = client.get("/api/countries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Testland"
    assert data[0]["iso_code"] == "TL"


def test_get_country_detail(client, sample_country_with_climate):
    country_id = sample_country_with_climate.id
    response = client.get(f"/api/countries/{country_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Testland"
    assert data["population"] == 1_000_000
    assert len(data["climate_data"]) == 1
    assert data["climate_data"][0]["metric_type"] == "temperature"
    assert data["climate_data"][0]["value"] == 25.5


def test_get_country_not_found(client):
    response = client.get("/api/countries/99999")
    assert response.status_code == 404


def test_search_countries(client, sample_country):
    response = client.get("/api/countries?search=test")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/api/countries?search=nonexistent")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_filter_by_region(client, sample_country):
    response = client.get("/api/countries?region=Test")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/api/countries?region=Other")
    assert response.status_code == 200
    assert len(response.json()) == 0

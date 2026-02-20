import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.climate_data import ClimateData
from app.models.country import Country

# Use a separate test database
TEST_DATABASE_URL = settings.DATABASE_URL.rsplit("/", 1)[0] + "/climate_tracker_test"


@pytest.fixture(scope="session")
def test_engine():
    """Create the test database and tables once per test session."""
    # Connect to default DB to create test DB
    base_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_engine(base_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        # Drop and recreate test DB
        conn.execute(text("DROP DATABASE IF EXISTS climate_tracker_test"))
        conn.execute(text("CREATE DATABASE climate_tracker_test"))
    admin_engine.dispose()

    engine = create_engine(TEST_DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Create a fresh DB session that rolls back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI test client with overridden DB dependency."""
    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_country(db_session):
    """Insert a sample country and return it."""
    country = Country(
        name="Testland",
        iso_code="TL",
        iso3_code="TLD",
        region="Test Region",
        capital_city="Testville",
        latitude=10.0,
        longitude=20.0,
        population=1_000_000,
    )
    db_session.add(country)
    db_session.flush()
    return country


@pytest.fixture
def sample_country_with_climate(db_session, sample_country):
    """Insert a sample country with climate data."""
    data = ClimateData(
        country_id=sample_country.id,
        date=datetime.date(2020, 1, 1),
        metric_type="temperature",
        value=25.5,
        unit="°C",
        source="Test Source",
    )
    db_session.add(data)
    db_session.flush()
    return sample_country

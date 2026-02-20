"""
Database seed script.

Usage: poetry run python -m scripts.seed

1. Countries — World Bank API
2. Temperature change from GHG — OWID CO2 dataset CSV (annual)
3. CO2 emissions — OWID CO2 dataset CSV (annual)
"""

import datetime
import os
import sys

import httpx
import pandas as pd
from sqlalchemy.orm import Session

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.climate_data import ClimateData
from app.models.country import Country

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".data")
OWID_CSV_PATH = os.path.join(DATA_DIR, "owid-co2-data.csv")
OWID_CSV_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"

WORLD_BANK_COUNTRIES_URL = "https://api.worldbank.org/v2/country?format=json&per_page=300"

# Regions that are aggregates, not real countries
AGGREGATE_CODES = {
    "1A", "S3", "B8", "V2", "Z4", "4E", "T4", "XC", "Z7", "7E", "T7",
    "EU", "F1", "XE", "XD", "XF", "ZT", "XH", "XI", "XG", "V3", "ZJ",
    "XJ", "T2", "XL", "XO", "XM", "XN", "ZQ", "XQ", "T3", "XP", "XU",
    "XY", "OE", "S4", "S2", "V4", "V1", "S1", "8S", "T5", "ZG", "ZF",
    "T6", "XT", "1W",
}


def ensure_owid_csv():
    """Download OWID CSV if not cached locally."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(OWID_CSV_PATH):
        print("  Downloading OWID CO2 dataset...")
        resp = httpx.get(OWID_CSV_URL, timeout=60, follow_redirects=True)
        resp.raise_for_status()
        with open(OWID_CSV_PATH, "wb") as f:
            f.write(resp.content)
        print(f"  Saved to {OWID_CSV_PATH}")
    else:
        print(f"  Using cached OWID CSV at {OWID_CSV_PATH}")
    return pd.read_csv(OWID_CSV_PATH)


def seed_countries(db: Session) -> dict[str, Country]:
    """Fetch countries from World Bank API and insert into DB."""
    existing = db.query(Country).count()
    if existing > 0:
        print(f"  Countries already seeded ({existing} records). Skipping.")
        countries = db.query(Country).all()
        return {c.iso_code: c for c in countries}

    print("  Fetching countries from World Bank API...")
    resp = httpx.get(WORLD_BANK_COUNTRIES_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # World Bank returns [metadata, data_array]
    raw_countries = data[1] if len(data) > 1 else []

    countries_map: dict[str, Country] = {}
    for item in raw_countries:
        iso2 = item.get("iso2Code", "")
        if not iso2 or len(iso2) != 2 or iso2 in AGGREGATE_CODES:
            continue
        # Skip if region info suggests it's an aggregate
        region = item.get("region", {})
        if region and region.get("id") == "NA":
            continue

        lat = None
        lng = None
        try:
            lat = float(item.get("latitude", "")) if item.get("latitude") else None
            lng = float(item.get("longitude", "")) if item.get("longitude") else None
        except (ValueError, TypeError):
            pass

        country = Country(
            name=item.get("name", ""),
            iso_code=iso2,
            iso3_code=item.get("id", ""),
            region=region.get("value", "") if region else None,
            capital_city=item.get("capitalCity", "") or None,
            latitude=lat,
            longitude=lng,
        )
        db.add(country)
        countries_map[iso2] = country

    db.commit()
    for c in countries_map.values():
        db.refresh(c)
    print(f"  Inserted {len(countries_map)} countries.")
    return countries_map


def _seed_owid_metric(
    db: Session,
    df: pd.DataFrame,
    iso3_to_country: dict[str, Country],
    owid_column: str,
    metric_type: str,
    unit: str,
):
    """Generic helper to seed a metric from the OWID CSV."""
    existing = db.query(ClimateData).filter(ClimateData.metric_type == metric_type).count()
    if existing > 0:
        print(f"  {metric_type} already seeded ({existing} records). Skipping.")
        return

    filtered = df[df[owid_column].notna() & df["iso_code"].notna()].copy()

    records = []
    for _, row in filtered.iterrows():
        iso3 = str(row["iso_code"]).strip()
        country = iso3_to_country.get(iso3)
        if not country:
            continue
        try:
            year = int(row["year"])
            value = float(row[owid_column])
            date = datetime.date(year, 1, 1)
            records.append(ClimateData(
                country_id=country.id,
                date=date,
                metric_type=metric_type,
                value=value,
                unit=unit,
                source="Our World in Data",
            ))
        except (ValueError, TypeError):
            continue

    if records:
        batch_size = 5000
        for i in range(0, len(records), batch_size):
            db.bulk_save_objects(records[i:i + batch_size])
            db.commit()

    print(f"  Inserted {len(records)} {metric_type} records.")


def main():
    print("Starting database seed...")
    db = SessionLocal()
    try:
        print("\n[1/3] Seeding countries...")
        countries = seed_countries(db)

        print("\n  Loading OWID dataset...")
        owid_df = ensure_owid_csv()
        iso3_to_country = {c.iso3_code: c for c in countries.values() if c.iso3_code}

        print("\n[2/3] Seeding temperature change data...")
        _seed_owid_metric(
            db, owid_df, iso3_to_country,
            owid_column="temperature_change_from_ghg",
            metric_type="temperature_change",
            unit="°C",
        )

        print("\n[3/3] Seeding CO2 emissions data...")
        _seed_owid_metric(
            db, owid_df, iso3_to_country,
            owid_column="co2",
            metric_type="co2_emissions",
            unit="Mt CO2",
        )

        print("\nSeed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()

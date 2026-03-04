"""Seed phase 3.1 additional climate data sources.

Data sources ingested:
1. CO2 per capita       — OWID CO2 dataset CSV (already cached)
2. Methane emissions    — OWID CO2 dataset CSV (already cached)
3. Forest area %        — World Bank API (AG.LND.FRST.ZS)
4. Sea level rise       — NOAA Laboratory for Satellite Altimetry (global)
5. Ocean SST anomaly    — NOAA Climate at a Glance (global)
6. EM-DAT disasters     — local CSV download required (see below)

EM-DAT instructions:
  1. Register at https://www.emdat.be/
  2. Download the "Public" CSV export for all countries/all years
  3. Save to .data/emdat.csv
  4. Re-run this script

Usage:
    poetry run python -m scripts.seed_extended
"""

import datetime
import io
import os
import sys
import time

import httpx
import pandas as pd
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.climate_data import ClimateData
from app.models.country import Country

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".data")
OWID_CSV_PATH = os.path.join(DATA_DIR, "owid-co2-data.csv")
EMDAT_CSV_PATH = os.path.join(DATA_DIR, "emdat.csv")

# NOAA Climate at a Glance — global ocean SST anomaly (annual, all months combined)
NOAA_CAG_OCEAN_URL = (
    "https://www.ncei.noaa.gov/cag/global/time-series/globe/ocean/ann/12/1880-2024.csv"
)

# NOAA Laboratory for Satellite Altimetry — global mean sea level (TOPEX/Jason/OSTM)
NOAA_SLR_URL = (
    "https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/"
    "LSA_SLR_timeseries_TOPEX_Jason123_OSTM_OST-6_Compressed.csv"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_existing(db: Session, metric_type: str) -> int:
    return db.query(ClimateData).filter(ClimateData.metric_type == metric_type).count()


def _build_iso3_map(db: Session) -> dict[str, Country]:
    return {c.iso3_code: c for c in db.query(Country).all() if c.iso3_code}


def _build_iso2_map(db: Session) -> dict[str, Country]:
    return {c.iso_code: c for c in db.query(Country).all()}


def _batch_insert(db: Session, records: list[ClimateData]) -> None:
    batch_size = 5000
    for i in range(0, len(records), batch_size):
        db.bulk_save_objects(records[i : i + batch_size])
        db.commit()


# ---------------------------------------------------------------------------
# 1. OWID metrics (co2_per_capita, methane)
# ---------------------------------------------------------------------------

def seed_owid_metric(
    db: Session,
    df: pd.DataFrame,
    iso3_map: dict[str, Country],
    owid_column: str,
    metric_type: str,
    unit: str,
) -> None:
    if _count_existing(db, metric_type) > 0:
        print(f"  {metric_type} already seeded. Skipping.")
        return

    filtered = df[df[owid_column].notna() & df["iso_code"].notna()].copy()
    records = []
    for _, row in filtered.iterrows():
        country = iso3_map.get(str(row["iso_code"]).strip())
        if not country:
            continue
        try:
            records.append(
                ClimateData(
                    country_id=country.id,
                    date=datetime.date(int(row["year"]), 1, 1),
                    metric_type=metric_type,
                    value=float(row[owid_column]),
                    unit=unit,
                    source="Our World in Data",
                )
            )
        except (ValueError, TypeError):
            continue

    _batch_insert(db, records)
    print(f"  Inserted {len(records)} {metric_type} records.")


# ---------------------------------------------------------------------------
# 2. World Bank — forest area % (AG.LND.FRST.ZS)
# ---------------------------------------------------------------------------

WB_FOREST_INDICATOR = "AG.LND.FRST.ZS"
WB_BASE = "https://api.worldbank.org/v2"


def _fetch_wb_pages(url: str) -> list[dict]:
    """Fetch all pages from a World Bank API endpoint."""
    results = []
    page = 1
    while True:
        resp = httpx.get(f"{url}&page={page}", timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if len(data) < 2 or not data[1]:
            break
        results.extend(data[1])
        meta = data[0]
        if page >= meta.get("pages", 1):
            break
        page += 1
        time.sleep(0.2)
    return results


def seed_forest_area(db: Session, iso2_map: dict[str, Country]) -> None:
    metric_type = "forest_area_pct"
    if _count_existing(db, metric_type) > 0:
        print(f"  {metric_type} already seeded. Skipping.")
        return

    print("  Fetching forest area data from World Bank API...")
    url = (
        f"{WB_BASE}/country/all/indicator/{WB_FOREST_INDICATOR}"
        f"?format=json&per_page=1000&date=1960:2023"
    )
    raw = _fetch_wb_pages(url)

    records = []
    for item in raw:
        if item.get("value") is None:
            continue
        country_info = item.get("country", {})
        iso2 = country_info.get("id", "")
        country = iso2_map.get(iso2)
        if not country:
            continue
        try:
            year = int(item["date"])
            records.append(
                ClimateData(
                    country_id=country.id,
                    date=datetime.date(year, 1, 1),
                    metric_type=metric_type,
                    value=float(item["value"]),
                    unit="% of land area",
                    source="World Bank (FAO)",
                )
            )
        except (ValueError, TypeError):
            continue

    _batch_insert(db, records)
    print(f"  Inserted {len(records)} {metric_type} records.")


# ---------------------------------------------------------------------------
# 3. NOAA Climate at a Glance — global ocean SST anomaly
# ---------------------------------------------------------------------------

def seed_ocean_temp(db: Session) -> None:
    metric_type = "ocean_temp_anomaly"
    if _count_existing(db, metric_type) > 0:
        print(f"  {metric_type} already seeded. Skipping.")
        return

    print("  Fetching ocean SST anomaly from NOAA Climate at a Glance...")
    try:
        resp = httpx.get(NOAA_CAG_OCEAN_URL, timeout=30, follow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"  WARNING: Could not fetch ocean SST data: {e}. Skipping.")
        return

    # NOAA CAG CSV has metadata rows before the actual data; data starts after "Year,Anomaly"
    text = resp.text
    data_start = text.find("Year,Anomaly")
    if data_start == -1:
        print("  WARNING: Unexpected NOAA CAG format. Skipping.")
        return

    df = pd.read_csv(io.StringIO(text[data_start:]))
    df.columns = df.columns.str.strip()

    records = []
    for _, row in df.iterrows():
        try:
            records.append(
                ClimateData(
                    country_id=None,  # global metric
                    date=datetime.date(int(row["Year"]), 1, 1),
                    metric_type=metric_type,
                    value=float(row["Anomaly"]),
                    unit="°C anomaly",
                    source="NOAA Climate at a Glance",
                )
            )
        except (ValueError, TypeError):
            continue

    _batch_insert(db, records)
    print(f"  Inserted {len(records)} {metric_type} records.")


# ---------------------------------------------------------------------------
# 4. NOAA satellite altimetry — global mean sea level rise
# ---------------------------------------------------------------------------

def seed_sea_level(db: Session) -> None:
    metric_type = "sea_level_rise_mm"
    if _count_existing(db, metric_type) > 0:
        print(f"  {metric_type} already seeded. Skipping.")
        return

    print("  Fetching sea level rise data from NOAA satellite altimetry...")
    try:
        resp = httpx.get(NOAA_SLR_URL, timeout=60, follow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"  WARNING: Could not fetch sea level data: {e}. Skipping.")
        return

    # The NOAA SLR CSV has a header section; data columns are decimal_year, msl (mm), ...
    text = resp.text
    lines = [ln for ln in text.splitlines() if not ln.startswith("HDR") and ln.strip()]
    if not lines:
        print("  WARNING: Empty sea level response. Skipping.")
        return

    try:
        df = pd.read_csv(io.StringIO("\n".join(lines)), header=0)
    except Exception as e:
        print(f"  WARNING: Could not parse sea level CSV: {e}. Skipping.")
        return

    # Column 1 is decimal year, column 2 is mean sea level (mm)
    if df.shape[1] < 2:
        print("  WARNING: Unexpected sea level CSV format. Skipping.")
        return

    df.columns = [c.strip() for c in df.columns]
    year_col = df.columns[0]
    msl_col = df.columns[1]

    # Aggregate to annual means (the CSV is monthly/bi-monthly)
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df[msl_col] = pd.to_numeric(df[msl_col], errors="coerce")
    df = df.dropna(subset=[year_col, msl_col])
    df["year_int"] = df[year_col].astype(int)
    annual = df.groupby("year_int")[msl_col].mean().reset_index()

    records = []
    for _, row in annual.iterrows():
        try:
            records.append(
                ClimateData(
                    country_id=None,  # global metric
                    date=datetime.date(int(row["year_int"]), 1, 1),
                    metric_type=metric_type,
                    value=float(row[msl_col]),
                    unit="mm (vs baseline)",
                    source="NOAA Laboratory for Satellite Altimetry",
                )
            )
        except (ValueError, TypeError):
            continue

    _batch_insert(db, records)
    print(f"  Inserted {len(records)} {metric_type} records.")


# ---------------------------------------------------------------------------
# 5. EM-DAT — natural disaster statistics per country per year
# ---------------------------------------------------------------------------

EMDAT_METRICS = {
    "disaster_count": ("count", "count"),
    "disaster_deaths": ("Total Deaths", "deaths"),
    "disaster_total_damage_usd": ("Total Damage, Adjusted ('000 US$)", "thousand USD"),
}

# EM-DAT column name variants (the export format has changed over versions)
EMDAT_DEATH_COLS = ["Total Deaths", "Total deaths", "Deaths"]
EMDAT_DAMAGE_COLS = [
    "Total Damage, Adjusted ('000 US$)",
    "Total Damage Adjusted ('000 US$)",
    "Reconstruction Costs, Adjusted ('000 US$)",
    "Total Damage ('000 US$)",
]
EMDAT_ISO_COLS = ["ISO", "iso", "ISO3"]
EMDAT_YEAR_COLS = ["Year", "year", "Start Year", "Dis Year"]


def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def seed_emdat(db: Session, iso3_map: dict[str, Country]) -> None:
    metrics = ["disaster_count", "disaster_deaths", "disaster_total_damage_usd"]
    if all(_count_existing(db, m) > 0 for m in metrics):
        print("  EM-DAT metrics already seeded. Skipping.")
        return

    if not os.path.exists(EMDAT_CSV_PATH):
        print(
            "  EM-DAT CSV not found at .data/emdat.csv.\n"
            "  To seed disaster data:\n"
            "    1. Register at https://www.emdat.be/\n"
            "    2. Download the public CSV for all countries/years\n"
            "    3. Save to .data/emdat.csv\n"
            "    4. Re-run this script"
        )
        return

    print(f"  Loading EM-DAT CSV from {EMDAT_CSV_PATH}...")
    df = pd.read_csv(EMDAT_CSV_PATH, encoding="latin-1", low_memory=False)

    iso_col = _find_col(df, EMDAT_ISO_COLS)
    year_col = _find_col(df, EMDAT_YEAR_COLS)
    death_col = _find_col(df, EMDAT_DEATH_COLS)
    damage_col = _find_col(df, EMDAT_DAMAGE_COLS)

    if not iso_col or not year_col:
        print("  WARNING: Could not find ISO or Year columns in EM-DAT CSV. Skipping.")
        return

    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df = df.dropna(subset=[iso_col, year_col])

    # Aggregate per country per year
    grouped = df.groupby([iso_col, year_col])

    count_records: list[ClimateData] = []
    death_records: list[ClimateData] = []
    damage_records: list[ClimateData] = []

    for (iso3, year), group in grouped:
        country = iso3_map.get(str(iso3).strip().upper())
        if not country:
            continue
        try:
            date = datetime.date(int(year), 1, 1)
        except (ValueError, OverflowError):
            continue

        if _count_existing(db, "disaster_count") == 0:
            count_records.append(
                ClimateData(
                    country_id=country.id,
                    date=date,
                    metric_type="disaster_count",
                    value=float(len(group)),
                    unit="count",
                    source="EM-DAT",
                )
            )

        if death_col and _count_existing(db, "disaster_deaths") == 0:
            deaths = pd.to_numeric(group[death_col], errors="coerce").sum()
            death_records.append(
                ClimateData(
                    country_id=country.id,
                    date=date,
                    metric_type="disaster_deaths",
                    value=float(deaths),
                    unit="deaths",
                    source="EM-DAT",
                )
            )

        if damage_col and _count_existing(db, "disaster_total_damage_usd") == 0:
            damage = pd.to_numeric(group[damage_col], errors="coerce").sum()
            damage_records.append(
                ClimateData(
                    country_id=country.id,
                    date=date,
                    metric_type="disaster_total_damage_usd",
                    value=float(damage),
                    unit="thousand USD",
                    source="EM-DAT",
                )
            )

    for records, name in [
        (count_records, "disaster_count"),
        (death_records, "disaster_deaths"),
        (damage_records, "disaster_total_damage_usd"),
    ]:
        if records:
            _batch_insert(db, records)
            print(f"  Inserted {len(records)} {name} records.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Starting phase 3.1 extended seed...")
    db = SessionLocal()
    try:
        iso3_map = _build_iso3_map(db)
        iso2_map = _build_iso2_map(db)

        if not os.path.exists(OWID_CSV_PATH):
            print("ERROR: OWID CSV not found. Run scripts/seed.py first.")
            sys.exit(1)

        print("\nLoading OWID dataset...")
        owid_df = pd.read_csv(OWID_CSV_PATH)

        print("\n[1/6] CO2 per capita (OWID)...")
        seed_owid_metric(
            db, owid_df, iso3_map,
            owid_column="co2_per_capita",
            metric_type="co2_per_capita",
            unit="t CO2/person",
        )

        print("\n[2/6] Methane emissions (OWID)...")
        seed_owid_metric(
            db, owid_df, iso3_map,
            owid_column="methane",
            metric_type="methane",
            unit="Mt CO2e",
        )

        print("\n[3/6] Forest area % (World Bank)...")
        seed_forest_area(db, iso2_map)

        print("\n[4/6] Ocean SST anomaly (NOAA Climate at a Glance)...")
        seed_ocean_temp(db)

        print("\n[5/6] Sea level rise (NOAA satellite altimetry)...")
        seed_sea_level(db)

        print("\n[6/6] EM-DAT disaster statistics...")
        seed_emdat(db, iso3_map)

        print("\nPhase 3.1 seed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()

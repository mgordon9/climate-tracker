"""Generate text descriptions and embeddings for all ClimateData rows.

Rows that already have an embedding are skipped (idempotent).

Run with:
    poetry run python -m scripts.embed_climate
"""

import os
import sys

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.climate_data import ClimateData
from app.models.country import Country

BATCH_SIZE = 512

_METRIC_TEMPLATES: dict[str, str] = {
    "temperature_change": "{country} temperature change from GHGs was {value:.2f}°C in {year}",
    "co2_emissions": "{country} emitted {value:.1f} Mt CO₂ in {year}",
    "co2_per_capita": "{country} CO₂ emissions per capita were {value:.2f} t/person in {year}",
    "methane": "{country} methane emissions were {value:.1f} Mt CO₂e in {year}",
    "land_use_change_co2": "{country} CO₂ from land-use change was {value:.1f} Mt in {year}",
    "forest_area_pct": "{country} had {value:.1f}% forest cover in {year}",
    "sea_level_rise_mm": "Global mean sea level was {value:.1f} mm above baseline in {year}",
    "ocean_temp_anomaly": (
        "Global ocean surface temperature anomaly was {value:.3f}°C in {year}"
    ),
    "disaster_count": "{country} had {value:.0f} recorded natural disasters in {year}",
    "disaster_deaths": "{country} natural disasters caused {value:.0f} deaths in {year}",
    "disaster_total_damage_usd": (
        "{country} natural disasters caused ${value:,.0f} thousand in economic damage in {year}"
    ),
}

_DEFAULT_TEMPLATE = "{country} {metric} was {value} {unit} in {year}"


def _describe(row: ClimateData, country_name: str) -> str:
    template = _METRIC_TEMPLATES.get(row.metric_type, _DEFAULT_TEMPLATE)
    return template.format(
        country=country_name,
        value=row.value,
        unit=row.unit,
        year=row.date.year,
        metric=row.metric_type.replace("_", " "),
    )


def embed_all(db: Session, model: SentenceTransformer) -> None:
    # Prefetch country names to avoid N+1 queries
    country_names: dict[int, str] = {
        c.id: c.name for c in db.query(Country.id, Country.name).all()  # type: ignore[arg-type]
    }

    total_processed = 0
    offset = 0

    while True:
        batch: list[ClimateData] = (
            db.query(ClimateData)
            .filter(ClimateData.embedding.is_(None))
            .order_by(ClimateData.id)
            .limit(BATCH_SIZE)
            .offset(offset)
            .all()
        )
        if not batch:
            break

        texts = [
            _describe(row, country_names.get(row.country_id, "Global") if row.country_id else "Global")
            for row in batch
        ]
        vectors = model.encode(texts, batch_size=64, show_progress_bar=False)

        for row, vec in zip(batch, vectors):
            row.embedding = vec.tolist()

        db.commit()
        total_processed += len(batch)
        print(f"  Embedded {total_processed} rows so far...")

        # After commit the rows have embeddings, so offset only needs to advance
        # if the batch was smaller than BATCH_SIZE (i.e., we're near the end).
        # Since we filter on embedding IS NULL and just committed embeddings,
        # offset stays at 0 — the next query will pick up remaining unembedded rows.

    print(f"Done. Embedded {total_processed} ClimateData rows total.")


def main() -> None:
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    db: Session = SessionLocal()
    try:
        unembedded = db.query(ClimateData).filter(ClimateData.embedding.is_(None)).count()
        print(f"Found {unembedded} ClimateData rows without embeddings.")
        if unembedded == 0:
            print("Nothing to do.")
            return
        embed_all(db, model)
    finally:
        db.close()


if __name__ == "__main__":
    main()

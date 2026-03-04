"""Generate embeddings for all ClimateData rows where embedding IS NULL."""
import sys

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.climate_data import ClimateData
from app.models.country import Country


def build_text(country_name: str, row: ClimateData) -> str:
    if row.metric_type == "temperature_change":
        return f"{country_name} temperature changed by {row.value:.2f}°C in {row.date.year} due to greenhouse gas emissions."
    if row.metric_type == "co2_emissions":
        return f"{country_name} emitted {row.value:.1f} Mt CO2 in {row.date.year}."
    return f"{country_name} {row.metric_type} was {row.value} {row.unit} in {row.date.year}."


def main() -> None:
    print("Loading model…")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    db: Session = SessionLocal()
    try:
        rows = (
            db.query(ClimateData, Country.name)
            .join(Country, ClimateData.country_id == Country.id)
            .filter(ClimateData.embedding == None)  # noqa: E711
            .all()
        )
        if not rows:
            print("No rows without embeddings found.")
            return

        print(f"Encoding {len(rows)} rows…")
        texts = [build_text(name, row) for row, name in rows]
        vectors = model.encode(texts, batch_size=256, show_progress_bar=True)

        batch_size = 1000
        for i in range(0, len(rows), batch_size):
            batch_rows = rows[i : i + batch_size]
            batch_vectors = vectors[i : i + batch_size]
            for (row, _), vec in zip(batch_rows, batch_vectors):
                row.embedding = vec.tolist()
            db.commit()
            print(f"Committed {min(i + batch_size, len(rows))}/{len(rows)}")

        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

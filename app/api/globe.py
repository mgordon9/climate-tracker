from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.country import GlobeCountry

router = APIRouter()


@router.get("/globe", response_model=list[GlobeCountry])
def get_globe_data(db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT
                c.id,
                c.name,
                c.iso_code,
                c.iso3_code,
                c.latitude,
                c.longitude,
                cd.value AS latest_temp_change
            FROM countries c
            LEFT JOIN LATERAL (
                SELECT value
                FROM climate_data
                WHERE country_id = c.id
                  AND metric_type = 'temperature_change'
                ORDER BY date DESC
                LIMIT 1
            ) cd ON true
            ORDER BY c.name
        """)
    ).fetchall()

    return [
        GlobeCountry(
            id=row.id,
            name=row.name,
            iso_code=row.iso_code,
            iso3_code=row.iso3_code,
            latitude=row.latitude,
            longitude=row.longitude,
            latest_temp_change=row.latest_temp_change,
        )
        for row in rows
    ]

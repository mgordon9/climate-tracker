from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.climate_data import ClimateData
from app.models.country import Country
from app.schemas.country import TimeSeries, TimeSeriesPoint

router = APIRouter()


def _build_time_series(country: Country, rows: list[ClimateData]) -> TimeSeries:
    unit = rows[0].unit if rows else ""
    metric = rows[0].metric_type if rows else ""
    return TimeSeries(
        country_id=country.id,
        country_name=country.name,
        iso_code=country.iso_code,
        metric=metric,
        unit=unit,
        data=[TimeSeriesPoint(year=r.date.year, value=r.value) for r in rows],
    )


@router.get("/countries/{country_id}/climate", response_model=TimeSeries)
def get_country_climate(
    country_id: int,
    metric: str = Query(..., description="Metric type, e.g. temperature_change"),
    start_year: int = Query(1900),
    end_year: int = Query(2100),
    db: Session = Depends(get_db),
):
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    rows = (
        db.query(ClimateData)
        .filter(
            ClimateData.country_id == country_id,
            ClimateData.metric_type == metric,
            ClimateData.date >= f"{start_year}-01-01",
            ClimateData.date <= f"{end_year}-12-31",
        )
        .order_by(ClimateData.date)
        .all()
    )
    return _build_time_series(country, rows)


@router.get("/compare", response_model=list[TimeSeries])
def compare_countries(
    country_ids: list[int] = Query(..., description="List of country IDs to compare"),
    metric: str = Query(..., description="Metric type"),
    start_year: int = Query(1900),
    end_year: int = Query(2100),
    db: Session = Depends(get_db),
):
    result = []
    for cid in country_ids:
        country = db.query(Country).filter(Country.id == cid).first()
        if not country:
            continue
        rows = (
            db.query(ClimateData)
            .filter(
                ClimateData.country_id == cid,
                ClimateData.metric_type == metric,
                ClimateData.date >= f"{start_year}-01-01",
                ClimateData.date <= f"{end_year}-12-31",
            )
            .order_by(ClimateData.date)
            .all()
        )
        result.append(_build_time_series(country, rows))
    return result

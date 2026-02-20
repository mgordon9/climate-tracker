from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.country import Country
from app.schemas.country import CountryDetail, CountryList

router = APIRouter()


@router.get("/countries", response_model=list[CountryList])
def list_countries(
    search: str | None = Query(None, description="Search by country name"),
    region: str | None = Query(None, description="Filter by region"),
    db: Session = Depends(get_db),
):
    query = db.query(Country)
    if search:
        query = query.filter(Country.name.ilike(f"%{search}%"))
    if region:
        query = query.filter(Country.region.ilike(f"%{region}%"))
    return query.order_by(Country.name).all()


@router.get("/countries/{country_id}", response_model=CountryDetail)
def get_country(country_id: int, db: Session = Depends(get_db)):
    country = (
        db.query(Country)
        .options(joinedload(Country.climate_data))
        .filter(Country.id == country_id)
        .first()
    )
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

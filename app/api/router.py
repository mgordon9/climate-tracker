from fastapi import APIRouter

from app.api.countries import router as countries_router
from app.api.health import router as health_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(countries_router, tags=["countries"])

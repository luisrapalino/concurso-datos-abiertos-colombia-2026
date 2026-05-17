from fastapi import APIRouter

from modules.health_indicators.interfaces.router import router as health_indicators_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_indicators_router)

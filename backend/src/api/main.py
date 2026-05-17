from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.router import api_v1_router
from config.settings import get_settings
from infrastructure.persistence.database import dispose_engine, init_engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    init_engine(settings.database_url)
    yield
    dispose_engine()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Territorial Epidemiological Intelligence API",
        version="1.0.0",
        description="REST API for territorial epidemiological indicators, risk, anomalies, and insights.",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    @application.get("/health", tags=["operations"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(api_v1_router, prefix="/api/v1")
    return application


app = create_app()

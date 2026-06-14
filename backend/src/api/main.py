from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.exception_handlers import register_exception_handlers
from api.v1.router import api_v1_router
from config.settings import get_settings
from infrastructure.persistence.database import dispose_engine, init_engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_engine(get_settings().database_url)
    yield
    dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Territorial Epidemiological Intelligence API",
        version="1.0.0",
        description=(
            "REST API for territorial epidemiological indicators, risk, anomalies, and insights."
        ),
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    register_exception_handlers(application)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health", tags=["operations"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(api_v1_router, prefix="/api/v1")
    return application


app = create_app()

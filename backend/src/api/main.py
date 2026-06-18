from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from api.exception_handlers import register_exception_handlers
from api.middleware.api_key import ApiKeyMiddleware
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.request_logging import RequestLoggingMiddleware
from api.middleware.security_headers import SecurityHeadersMiddleware
from api.v1.router import api_v1_router
from config.settings import get_settings
from infrastructure.logging.setup import configure_logging
from infrastructure.metrics.registry import request_metrics
from infrastructure.persistence.database import dispose_engine, init_engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging(json_logs=get_settings().log_json)
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

    application.add_middleware(ApiKeyMiddleware, api_key=settings.api_key)
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    if settings.rate_limit_enabled:
        application.add_middleware(
            RateLimitMiddleware,
            max_requests=settings.rate_limit_per_minute,
            window_seconds=60,
        )
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

    @application.get("/metrics", tags=["operations"], response_class=PlainTextResponse)
    def metrics() -> str:
        return (
            "# HELP epintel_http_requests_total Total HTTP requests served\n"
            "# TYPE epintel_http_requests_total counter\n"
            f"epintel_http_requests_total {request_metrics.total_requests}\n"
            "# HELP epintel_http_errors_total Total HTTP 5xx responses\n"
            "# TYPE epintel_http_errors_total counter\n"
            f"epintel_http_errors_total {request_metrics.total_errors}\n"
        )

    application.include_router(api_v1_router, prefix="/api/v1")
    return application


app = create_app()

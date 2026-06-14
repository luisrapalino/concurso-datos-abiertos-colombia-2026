import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from infrastructure.metrics.registry import request_metrics


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id", uuid.uuid4().hex)
        start = time.perf_counter()
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )
        logger = structlog.get_logger("api.request")
        logger.info("request_started")
        try:
            response = await call_next(request)
        except Exception:
            request_metrics.record_request(is_error=True)
            logger.exception("request_failed")
            raise
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        request_metrics.record_request(is_error=response.status_code >= 500)
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        response.headers["X-Request-Id"] = request_id
        return response

"""Optional API key protection for versioned API routes."""

from __future__ import annotations

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Require X-API-Key when API_KEY is configured (institutional deployments)."""

    def __init__(self, app, *, api_key: str | None) -> None:
        super().__init__(app)
        self._api_key = api_key

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if not self._api_key or not self._requires_auth(request.url.path):
            return await call_next(request)

        provided = request.headers.get("X-API-Key") or request.query_params.get("api_key")
        if provided != self._api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "code": "unauthorized",
                    "message": "Valid API key required for this endpoint.",
                },
            )
        return await call_next(request)

    @staticmethod
    def _requires_auth(path: str) -> bool:
        if not path.startswith("/api/v1"):
            return False
        return path not in {"/api/v1/openapi.json"}

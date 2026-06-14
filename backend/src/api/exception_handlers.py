from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from shared.errors import ApiErrorDetail, ApiErrorResponse
from shared.exceptions import DomainError, EntityNotFoundError, ServiceUnavailableError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(_request: Request, exc: EntityNotFoundError) -> JSONResponse:
        payload = ApiErrorResponse(
            code="not_found",
            message=str(exc),
            details=[ApiErrorDetail(field=exc.entity, message=exc.identifier)],
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=payload.model_dump(),
        )

    @app.exception_handler(ServiceUnavailableError)
    async def service_unavailable_handler(
        _request: Request,
        exc: ServiceUnavailableError,
    ) -> JSONResponse:
        payload = ApiErrorResponse(
            code="service_unavailable",
            message=str(exc),
            details=[ApiErrorDetail(field=exc.service, message=exc.reason or "unavailable")],
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload.model_dump(),
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        payload = ApiErrorResponse(code="domain_error", message=str(exc))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=payload.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ApiErrorDetail(
                field=".".join(str(part) for part in error.get("loc", []) if part != "body"),
                message=error.get("msg", "Invalid value"),
            )
            for error in exc.errors()
        ]
        payload = ApiErrorResponse(
            code="validation_error",
            message="Request validation failed.",
            details=details,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=payload.model_dump(),
        )

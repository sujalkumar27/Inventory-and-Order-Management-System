"""Custom exceptions and global handlers producing a consistent error envelope."""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("ioms")


class AppException(Exception):
    """Base application error -> {success: false, message: ...}."""

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT


class ValidationAppError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InsufficientInventoryError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST


class AuthError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN


def _error(message: str, status_code: int, errors=None) -> JSONResponse:
    body = {"success": False, "message": message}
    if errors is not None:
        body["errors"] = errors
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _app_exc(_: Request, exc: AppException):
        return _error(exc.message, exc.status_code)

    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(_: Request, exc: StarletteHTTPException):
        return _error(str(exc.detail), exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validation_exc(_: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return _error("Validation failed", status.HTTP_422_UNPROCESSABLE_ENTITY, errors)

    @app.exception_handler(IntegrityError)
    async def _integrity_exc(_: Request, exc: IntegrityError):
        return _error("Database integrity error", status.HTTP_409_CONFLICT)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        # Log the full traceback server-side; never leak internals to the client.
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return _error("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

"""Global exception handlers translating errors to consistent JSON responses."""
import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import JWTError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger("app.errors")


class AppError(Exception):
    """Base application error with HTTP-friendly metadata."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"

    def __init__(self, message: str, *, code: Optional[str] = None, details: Any = None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.details = details


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"


class ValidationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"


def _error_payload(
    code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Any = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"error": {"code": code, "message": message}}
    if request_id:
        payload["error"]["request_id"] = request_id
    if details is not None:
        payload["error"]["details"] = details
    return payload


async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(
            exc.code, exc.message, getattr(request.state, "request_id", None), exc.details
        ),
    )


async def _http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        429: "rate_limited",
    }
    code = code_map.get(exc.status_code, "http_error")
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(
            code, message, getattr(request.state, "request_id", None)
        ),
    )


async def _validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_payload(
            "validation_error",
            "Request validation failed",
            getattr(request.state, "request_id", None),
            exc.errors(),
        ),
    )


async def _jwt_error_handler(request: Request, exc: JWTError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=_error_payload(
            "invalid_token",
            "Invalid or expired token",
            getattr(request.state, "request_id", None),
        ),
    )


async def _integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    logger.warning("integrity_error: %s", exc.orig)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_error_payload(
            "integrity_error",
            "Database integrity constraint violated",
            getattr(request.state, "request_id", None),
        ),
    )


async def _sqlalchemy_error_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    logger.exception("database_error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload(
            "database_error",
            "An unexpected database error occurred",
            getattr(request.state, "request_id", None),
        ),
    )


async def _unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.exception("unhandled_exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload(
            "internal_error",
            "An unexpected error occurred",
            getattr(request.state, "request_id", None),
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(JWTError, _jwt_error_handler)
    app.add_exception_handler(IntegrityError, _integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, _sqlalchemy_error_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)

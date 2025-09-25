"""
Error handling middleware
"""
import uuid
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY
from pydantic import ValidationError
import traceback

from api.utils.responses import create_error_response

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            return response

        except HTTPException as exc:
            # Handle HTTP exceptions (these are expected)
            return JSONResponse(
                status_code=exc.status_code,
                content=create_error_response(
                    error="HTTP_ERROR",
                    message=exc.detail,
                    request_id=request_id,
                    status_code=exc.status_code
                )
            )

        except ValidationError as exc:
            # Handle Pydantic validation errors
            details = []
            for error in exc.errors():
                details.append({
                    "field": " -> ".join(str(x) for x in error["loc"]),
                    "message": error["msg"],
                    "code": error["type"]
                })

            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content=create_error_response(
                    error="VALIDATION_ERROR",
                    message="Input validation failed",
                    details=details,
                    request_id=request_id,
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY
                )
            )

        except Exception as exc:
            # Handle unexpected exceptions
            logger.error(
                f"Unhandled exception in request {request_id}: {exc}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "traceback": traceback.format_exc()
                }
            )

            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content=create_error_response(
                    error="INTERNAL_SERVER_ERROR",
                    message="An unexpected error occurred. Please try again later.",
                    request_id=request_id,
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR
                )
            )
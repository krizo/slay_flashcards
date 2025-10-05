"""
Request logging middleware
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response  # pylint: disable=import-error
from starlette.middleware.base import BaseHTTPMiddleware  # pylint: disable=import-error

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log incoming request
        request_id = getattr(request.state, "request_id", "unknown")
        logger.info(
            "Incoming request: %s %s",
            request.method,
            request.url,
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            "Request completed: %s in %.3fs",
            response.status_code,
            process_time,
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
            },
        )

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id

        return response

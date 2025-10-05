"""
Rate limiting middleware
"""

import logging
import time
from collections import defaultdict, deque
from typing import Callable, Dict

from fastapi import HTTPException, Request, Response, status  # pylint: disable=import-error
from fastapi.responses import JSONResponse  # pylint: disable=import-error
from starlette.middleware.base import BaseHTTPMiddleware  # pylint: disable=import-error

from api.utils.responses import create_error_response

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""

    def __init__(self, app, calls: int = 100, period: int = 60, per_user: bool = True, storage_backend: str = "memory"):  # pylint: disable=too-many-positional-arguments
        """
        Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            calls: Number of calls allowed per period
            period: Time period in seconds
            per_user: If True, limit per user; if False, limit per IP
            storage_backend: Storage backend ('memory' or 'redis')
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.per_user = per_user
        self.storage_backend = storage_backend

        # In-memory storage for development
        self._memory_storage: Dict[str, deque] = defaultdict(deque)

        # Redis client (if using Redis backend)
        self._redis_client = None
        if storage_backend == "redis":
            self._setup_redis()

    def _setup_redis(self):
        """Setup Redis client for rate limiting."""
        try:
            import redis  # pylint: disable=import-outside-toplevel

            from api.api_config import settings  # pylint: disable=import-outside-toplevel

            self._redis_client = redis.from_url(settings.redis_url)
        except ImportError:
            logger.warning("Redis not available, falling back to memory storage")
            self.storage_backend = "memory"
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to connect to Redis: %s, falling back to memory storage", e)
            self.storage_backend = "memory"

    def _get_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting (user ID or IP)."""
        if self.per_user:
            # Try to get user from JWT token
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                try:
                    import jwt  # pylint: disable=import-outside-toplevel,import-error

                    from api.api_config import settings  # pylint: disable=import-outside-toplevel

                    token = auth_header.split(" ")[1]
                    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
                    user_id = payload.get("user_id")
                    if user_id:
                        return f"user:{user_id}"
                except Exception:  # pylint: disable=broad-exception-caught
                    pass

        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        return f"ip:{client_ip}"

    def _get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit key."""
        return f"rate_limit:{identifier}:{endpoint}"

    def _is_rate_limited_memory(self, key: str) -> tuple[bool, int, int]:
        """Check rate limit using memory storage."""
        now = time.time()
        window_start = now - self.period

        # Clean old entries
        while self._memory_storage[key] and self._memory_storage[key][0] < window_start:
            self._memory_storage[key].popleft()

        current_calls = len(self._memory_storage[key])

        if current_calls >= self.calls:
            # Rate limited
            oldest_call = self._memory_storage[key][0] if self._memory_storage[key] else now
            reset_time = int(oldest_call + self.period)
            return True, current_calls, reset_time
        # Not rate limited, add current request
        self._memory_storage[key].append(now)
        return False, current_calls + 1, int(now + self.period)

    def _is_rate_limited_redis(self, key: str) -> tuple[bool, int, int]:
        """Check rate limit using Redis storage."""
        if not self._redis_client:
            return self._is_rate_limited_memory(key)

        try:
            pipe = self._redis_client.pipeline()
            now = time.time()
            window_start = now - self.period

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Count current entries
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {str(now): now})
            # Set expiration
            pipe.expire(key, self.period + 1)

            results = pipe.execute()
            current_calls = results[1]

            if current_calls >= self.calls:
                # Rate limited
                reset_time = int(now + self.period)
                return True, current_calls, reset_time
            return False, current_calls + 1, int(now + self.period)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Redis rate limiting error: %s", e)
            # Fallback to memory storage
            return self._is_rate_limited_memory(key)

    def _is_rate_limited(self, key: str) -> tuple[bool, int, int]:
        """Check if request should be rate limited."""
        if self.storage_backend == "redis":
            return self._is_rate_limited_redis(key)
        return self._is_rate_limited_memory(key)

    def _get_endpoint(self, request: Request) -> str:
        """Get endpoint identifier for rate limiting."""
        path = request.url.path
        method = request.method
        return f"{method}:{path}"

    def _should_skip_rate_limiting(self, request: Request) -> bool:
        """Check if request should skip rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.yaml"]:
            return True

        # Skip for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return True

        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""

        # Skip rate limiting for certain endpoints
        if self._should_skip_rate_limiting(request):
            return await call_next(request)

        # Get identifier and endpoint
        identifier = self._get_identifier(request)
        endpoint = self._get_endpoint(request)
        key = self._get_rate_limit_key(identifier, endpoint)

        # Check rate limit
        is_limited, current_calls, reset_time = self._is_rate_limited(key)

        if is_limited:
            # Rate limited - return 429 Too Many Requests
            logger.warning("Rate limit exceeded for %s on %s", identifier, endpoint)

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=create_error_response(
                    error="RATE_LIMIT_EXCEEDED",
                    message=f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds.",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                ),
                headers={
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(self.period),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = max(0, self.calls - current_calls)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response


class EndpointRateLimiter:
    """Decorator for endpoint-specific rate limiting."""

    def __init__(self, calls: int = 10, period: int = 60):
        """
        Initialize endpoint rate limiter.

        Args:
            calls: Number of calls allowed per period
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self._storage: Dict[str, deque] = defaultdict(deque)

    def __call__(self, func):
        """Decorator function."""

        async def wrapper(request: Request, *args, **kwargs):
            # Get client identifier
            client_ip = request.client.host if request.client else "unknown"

            # Check rate limit
            now = time.time()
            window_start = now - self.period
            key = f"{func.__name__}:{client_ip}"

            # Clean old entries
            while self._storage[key] and self._storage[key][0] < window_start:
                self._storage[key].popleft()

            if len(self._storage[key]) >= self.calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Rate limit exceeded for {func.__name__}"
                )

            # Add current request
            self._storage[key].append(now)

            # Call original function
            return await func(request, *args, **kwargs)

        return wrapper


# Decorator instances for common rate limits
strict_rate_limit = EndpointRateLimiter(calls=5, period=60)  # 5 calls per minute
moderate_rate_limit = EndpointRateLimiter(calls=20, period=60)  # 20 calls per minute
loose_rate_limit = EndpointRateLimiter(calls=100, period=60)  # 100 calls per minute


def rate_limit(calls: int = 10, period: int = 60):
    """
    Custom rate limit decorator.

    Args:
        calls: Number of calls allowed per period
        period: Time period in seconds

    Returns:
        Rate limiting decorator
    """
    return EndpointRateLimiter(calls=calls, period=period)

"""Rate limiting utilities."""

from datetime import datetime, timedelta
from typing import Dict, List

from starlette.responses import JSONResponse

from app.utils.error_handler import create_error_response


class RateLimiter:
    """Rate limiter implementation."""

    def __init__(self):
        """Initialize rate limiter."""
        self._requests: Dict[str, List[datetime]] = {}

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if a key is rate limited."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)

        # Clean up old requests
        if key in self._requests:
            self._requests[key] = [
                req_time for req_time in self._requests[key] if req_time > window_start
            ]
        else:
            self._requests[key] = []

        # Check rate limit
        if len(self._requests[key]) >= max_requests:
            return True

        # Add new request
        self._requests[key].append(now)
        return False


# Global rate limiter instance
limiter = RateLimiter()


def rate_limit(max_requests: int, window_seconds: int = 60):
    """Rate limiting decorator."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get client IP from request
            request = None
            for arg in args:
                if hasattr(arg, "client"):
                    request = arg

            if not request:
                return await func(*args, **kwargs)

            key = f"{request.client.host}:{func.__name__}"
            if limiter.is_rate_limited(key, max_requests, window_seconds):
                return JSONResponse(
                    status_code=429,
                    content=create_error_response(
                        code="rate_limit_exceeded",
                        message="Too many requests. Please try again later.",
                    ),
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator

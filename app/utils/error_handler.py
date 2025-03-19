"""Error handling utilities."""

import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type

from fastapi import HTTPException, status

from app.schemas.base_schema import ErrorDetailSchema as ErrorDetail
from app.utils.exceptions import InvalidInputException, NotFoundException, ServiceError
from app.utils.metrics import ErrorMetrics

logger = logging.getLogger(__name__)
metrics = ErrorMetrics()


class CustomException(Exception):
    """Base exception class for application-specific errors."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AppError(Exception):
    """Base application error with metrics."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        metrics.increment_error(error_code)
        logger.error(f"{error_code}: {message}", extra=self.details)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


def handle_service_error(func):
    """Decorator to handle service errors."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTPExceptions as they are already properly formatted
            raise
        except NotFoundException as e:
            logger.error(f"Not found: {str(e)}")
            metrics.increment_error("not_found")
            raise HTTPException(
                status_code=404,
                detail=ErrorDetail(
                    code="not_found",
                    message=str(e),
                    details=e.details if hasattr(e, "details") else None,
                ).dict(),
            )
        except InvalidInputException as e:
            logger.error(f"Invalid input: {str(e)}")
            metrics.increment_error("invalid_input")
            raise HTTPException(
                status_code=400,
                detail=ErrorDetail(
                    code="invalid_input",
                    message=str(e),
                    details=e.details if hasattr(e, "details") else None,
                ).dict(),
            )
        except ServiceError as e:
            error_type = e.__class__.__name__
            logger.error(f"{error_type}: {str(e)}")
            metrics.increment_error(error_type.lower())
            raise HTTPException(
                status_code=e.status_code,
                detail=ErrorDetail(
                    code=error_type.lower(),
                    message=str(e),
                    details=e.details if hasattr(e, "details") else None,
                ).dict(),
            )
        except ValueError as e:
            logger.error(f"Value error: {str(e)}")
            metrics.increment_error("value_error")
            raise HTTPException(
                status_code=400,
                detail=ErrorDetail(code="value_error", message=str(e)).dict(),
            )
        except Exception as e:
            logger.error(f"Unexpected service error: {str(e)}")
            metrics.increment_error("unexpected_service_error")
            raise HTTPException(
                status_code=500,
                detail=ErrorDetail(code="unexpected_error", message=str(e)).dict(),
            )

    return wrapper


def handle_exception(func: Callable) -> Callable:
    """Decorator for handling exceptions in routes."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except CustomException as e:
            logger.error(f"Custom error: {str(e)}")
            raise HTTPException(status_code=e.status_code, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    return wrapper


def handle_exceptions(error_map: Dict[Type[Exception], int] = None):
    """Enhanced exception handler with metrics."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AppError as e:
                metrics.increment_error(e.error_code)
                raise HTTPException(
                    status_code=e.status_code,
                    detail={"error_code": e.error_code, "message": str(e)},
                )
            except Exception as e:
                metrics.increment_error("unexpected_error")
                logger.exception("Unexpected error")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"error_code": "UNEXPECTED_ERROR", "message": str(e)},
                )

        return wrapper

    return decorator


class SchedulingError(ServiceError):
    """Exception raised for errors in the scheduling service."""

    def __init__(self, message: str, code: str = "SCHEDULING_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


def create_error_response(error_detail: ErrorDetail, status_code: int = 400) -> HTTPException:
    """Create a standardized error response."""
    return HTTPException(status_code=status_code, detail=error_detail.dict())


def create_error_detail(code: str, message: str, details: Optional[Any] = None) -> ErrorDetail:
    """Create an error detail object."""
    return ErrorDetail(code=code, message=message, details=details)


__all__ = [
    "AppError",
    "CustomException",
    "ServiceError",
    "InvalidInputException",
    "NotFoundException",
    "handle_exceptions",
    "handle_exception",
    "handle_service_error",
]

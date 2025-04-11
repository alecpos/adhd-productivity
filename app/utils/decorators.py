"""Utility decorators."""

from functools import wraps
from typing import Any, Callable, TypeVar
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.utils.concurrency import with_concurrency_control

T = TypeVar("T")


def handle_service_error(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle service errors and convert them to HTTPExceptions."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected service error: {str(e)}")

    return wrapper

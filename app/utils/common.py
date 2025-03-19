"""Common utility functions."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
from uuid import UUID

import pytz
from fastapi import HTTPException

logger = logging.getLogger(__name__)


# Date/Time Utilities
def get_datetime_range(date: datetime, timezone: str) -> Tuple[datetime, datetime]:
    """Get start and end datetime for a given date in a timezone."""
    tz = pytz.timezone(timezone)
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return tz.localize(start), tz.localize(end)


def parse_datetime(dt_str: str, timezone: str) -> datetime:
    """Parse datetime string with timezone."""
    tz = pytz.timezone(timezone)
    dt = datetime.fromisoformat(dt_str)
    return tz.localize(dt) if dt.tzinfo is None else dt


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


# Validation Utilities
def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID string."""
    try:
        UUID(uuid_str)
        return True
    except ValueError:
        return False


def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Validate that start_date is before end_date."""
    return start_date < end_date


def validate_pagination(page: int, size: int, max_size: int = 100) -> Tuple[int, int]:
    """Validate and normalize pagination parameters."""
    page = max(1, page)
    size = max(1, min(size, max_size))
    return page, size


# Data Processing Utilities
def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def paginate_list(items: List[Any], page: int, size: int) -> Tuple[List[Any], int]:
    """Paginate a list of items."""
    start = (page - 1) * size
    end = start + size
    return items[start:end], len(items)


# Error Handling Utilities
class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, error_code: str, status_code: int = 400):
        """Initialize AppError."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


def handle_exceptions(func):
    """Decorator to handle common exceptions."""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError as e:
            raise HTTPException(status_code=e.status_code, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    return wrapper

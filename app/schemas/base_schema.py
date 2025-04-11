"""Base Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class BaseSchema(BaseModel):
    """Base schema with common configurations.

    All schemas should inherit from this to get:
    - ORM mode enabled
    - UUID field handling
    - Datetime field handling
    """
    model_config = ConfigDict(from_attributes=True)


class UUIDSchema(BaseSchema):
    """Schema with UUID primary key."""
    id: UUID


class TimestampedSchema(UUIDSchema):
    """Schema with UUID and timestamps."""
    created_at: datetime
    updated_at: datetime


class BaseResponse(BaseModel):
    """Base response schema."""

    data: Any
    message: str
    error: Optional[str] = None
    details: Optional[Dict] = None


class ErrorDetailSchema(BaseSchema):
    """Schema for error details."""

    code: str = Field(..., description="Error code identifying the type of error")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema for paginated responses."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class TimeRange(BaseSchema):
    """Schema for time range."""

    start: datetime
    end: datetime

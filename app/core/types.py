"""Common types used across the application."""
from uuid import UUID

from pydantic import Field

from app.schemas.base_schema import BaseSchema


class UUIDSchema(BaseSchema):
    """UUID schema."""

    id: UUID = Field(..., description="Unique identifier")


class NoneSchema(BaseSchema):
    """Schema for None type returns."""
    pass

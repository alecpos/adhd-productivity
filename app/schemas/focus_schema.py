"""Focus session schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base_schema import BaseSchema, TimestampedSchema
from app.schemas.shared_components_schema import Break, EnvironmentalFactors


class FocusSessionBase(BaseSchema):
    """Base schema for focus sessions."""

    user_id: UUID
    task_id: Optional[UUID] = None
    duration: int = Field(..., description="Duration in minutes", ge=1)
    focus_level: int = Field(..., description="Focus level from 1-10", ge=1, le=10)
    energy_level: int = Field(..., description="Energy level from 1-10", ge=1, le=10)
    activity_type: str = Field(..., description="Type of activity being focused on")
    environment: Optional[EnvironmentalFactors] = None
    breaks: Optional[List[Break]] = None
    notes: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class FocusSessionCreateSchema(FocusSessionBase):
    """Schema for creating a focus session."""
    pass


class FocusSessionUpdate(BaseSchema):
    """Schema for updating a focus session."""

    focus_level: Optional[int] = Field(None, description="Focus level from 1-10", ge=1, le=10)
    energy_level: Optional[int] = Field(None, description="Energy level from 1-10", ge=1, le=10)
    notes: Optional[str] = None
    productivity_score: Optional[int] = Field(None, description="Productivity score from 1-10", ge=1, le=10)
    meta_data: Optional[Dict[str, Any]] = None


class FocusSessionSchema(FocusSessionBase, TimestampedSchema):
    """Schema for focus session responses."""

    status: str = Field(..., description="Current status of the focus session")
    start_time: datetime
    end_time: Optional[datetime] = None
    productivity_score: Optional[int] = Field(None, description="Productivity score from 1-10", ge=1, le=10)
    total_breaks: int = Field(0, description="Total number of breaks taken")
    total_break_duration: int = Field(0, description="Total break duration in minutes")
    actual_focus_duration: int = Field(0, description="Actual focus duration in minutes")


__all__ = [
    "FocusSessionSchema",
    "FocusSessionCreateSchema",
    "FocusSessionUpdate",
]

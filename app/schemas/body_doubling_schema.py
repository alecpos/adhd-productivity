"""Body doubling schemas module."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from app.models.enums_model import (
    SessionType,
    SessionStatus,
    InteractionType,
    ActivityType,
    EnergyLevel,
)
from app.schemas.base_schema import BaseSchema, TimestampedSchema


class EnvironmentDataSchema(BaseSchema):
    """Environment data schema."""
    noise_level: Optional[int] = Field(None, ge=1, le=10)
    lighting: Optional[int] = Field(None, ge=1, le=10)
    temperature: Optional[float] = None
    location: Optional[str] = None
    social_context: Optional[str] = None
    distractions: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class InteractionSchema(BaseSchema):
    """Interaction schema."""
    time: datetime
    type: InteractionType
    content: str = Field(..., min_length=1, max_length=500)
    duration: Optional[int] = Field(None, ge=0)  # seconds
    effectiveness: Optional[int] = Field(None, ge=1, le=10)

    model_config = ConfigDict(from_attributes=True)


class BreakSchema(BaseSchema):
    """Break schema."""
    start_time: datetime
    duration: int = Field(..., description="Duration in minutes", ge=1)
    type: str = Field(..., min_length=1, max_length=50)
    effectiveness: Optional[int] = Field(None, ge=1, le=10)

    model_config = ConfigDict(from_attributes=True)


class MilestoneSchema(BaseSchema):
    """Milestone schema."""
    time: datetime
    description: str = Field(..., min_length=1, max_length=200)
    completed: bool = False
    completion_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProgressUpdateSchema(BaseSchema):
    """Progress update schema."""
    time: datetime
    progress: float = Field(..., ge=0, le=1)
    notes: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class SessionFeedbackSchema(BaseSchema):
    """Schema for session feedback."""
    session_id: UUID
    user_id: UUID
    feedback_points: List[Dict[str, Any]]
    average_focus_level: float
    average_productivity: float
    average_distraction_level: float
    final_rating: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class GroupSessionSchema(BaseSchema):
    """Information about a group session."""
    session_id: UUID
    host_id: UUID
    topic: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    status: SessionStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_participants: int = Field(..., ge=2, le=10)
    current_participants: List[UUID]
    pending_requests: List[Dict[str, Any]]
    environment: Optional[Dict[str, Any]] = None
    activity_type: ActivityType
    duration_minutes: Optional[int] = Field(None, ge=5)

    model_config = ConfigDict(from_attributes=True)


class SessionAnalyticsSchema(BaseSchema):
    """Analytics for body doubling sessions."""
    user_id: UUID
    total_sessions: int
    total_duration: int  # in minutes
    completion_rate: float
    most_productive_times: List[str]
    preferred_activity_types: List[ActivityType]
    preferred_session_types: List[SessionType]
    average_focus_rating: float
    average_productivity_rating: float
    average_session_duration: int  # in minutes

    model_config = ConfigDict(from_attributes=True)


class CreateBodyDoublingSchema(BaseSchema):
    """Schema for creating a body doubling session."""
    user_id: UUID
    host_id: UUID
    session_type: SessionType
    activity_type: ActivityType
    planned_duration: int = Field(..., description="Duration in minutes", ge=15, le=240)
    max_participants: int = Field(default=2, description="Maximum number of participants", ge=2, le=10)
    description: Optional[str] = Field(None, max_length=500)
    energy_level: Optional[EnergyLevel] = None
    environment_data: Optional[EnvironmentDataSchema] = None

    model_config = ConfigDict(from_attributes=True)


class BodyDoublingSchema(TimestampedSchema):
    """Schema for body doubling session."""
    id: UUID
    host_id: UUID
    session_type: SessionType
    activity_type: ActivityType
    status: SessionStatus
    planned_duration: int
    actual_duration: Optional[int] = None
    description: Optional[str] = None
    energy_level: Optional[EnergyLevel] = None
    environment_data: Optional[EnvironmentDataSchema] = None
    participants: List[UUID] = Field(default_factory=list)
    interactions: List[InteractionSchema] = Field(default_factory=list)
    breaks: List[BreakSchema] = Field(default_factory=list)
    productivity_score: Optional[float] = Field(None, ge=0, le=10)
    feedback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BodyDoublingResponseSchema(BaseSchema):
    """Schema for body doubling response."""
    success: bool
    message: str
    data: BodyDoublingSchema

    model_config = ConfigDict(from_attributes=True)


class UpdateBodyDoublingSchema(BaseSchema):
    """Schema for updating a body doubling session."""
    session_type: Optional[SessionType] = None
    status: Optional[SessionStatus] = None
    activity_type: Optional[ActivityType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=5)
    partner_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    host_id: Optional[UUID] = None
    preferences: Optional[Dict[str, Any]] = None
    goals: Optional[List[str]] = None
    task_description: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class BodyDoublingListSchema(BaseSchema):
    """Schema for list of body doubling sessions."""
    sessions: List[BodyDoublingResponseSchema]

    model_config = ConfigDict(from_attributes=True)


class BodyDoublingStatsSchema(BaseSchema):
    """Schema for body doubling statistics."""
    total_sessions: int = Field(..., ge=0)
    total_duration: int = Field(..., ge=0)
    average_duration: float = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class BodyDoublingTrendsSchema(BaseSchema):
    """Schema for body doubling trends."""
    weekly_sessions: int = Field(..., ge=0)
    monthly_sessions: int = Field(..., ge=0)
    completion_rate: float = Field(..., ge=0, le=1)

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "EnvironmentDataSchema",
    "InteractionSchema",
    "BreakSchema",
    "MilestoneSchema",
    "ProgressUpdateSchema",
    "SessionFeedbackSchema",
    "GroupSessionSchema",
    "SessionAnalyticsSchema",
    "BodyDoublingSchema",
    "CreateBodyDoublingSchema",
    "UpdateBodyDoublingSchema",
    "BodyDoublingResponseSchema",
    "BodyDoublingListSchema",
    "BodyDoublingStatsSchema",
    "BodyDoublingTrendsSchema"
]

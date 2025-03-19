"""Hyperfocus schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, ValidationInfo

from app.models.enums_model import (
    HyperfocusSessionStatus,
    HyperfocusTaskType,
    SessionType,
    SessionStatus,
    ActivityType,
    EnergyLevel,
)


class SessionStatusSchema(str, Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    PAUSED = "paused"


class TaskTypeSchema(str, Enum):
    """Task type enumeration."""

    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    LEARNING = "learning"
    CODING = "coding"
    WRITING = "writing"
    RESEARCH = "research"
    PLANNING = "planning"
    OTHER = "other"


class BreakSchema(BaseModel):
    """Break schema."""

    start_time: datetime
    duration: int = Field(..., description="Duration in minutes", ge=1)
    type: str = Field(..., min_length=1, max_length=50)
    effectiveness: Optional[int] = Field(None, ge=1, le=10)


class InterruptionSchema(BaseModel):
    """Interruption schema."""

    time: datetime
    type: str = Field(..., min_length=1, max_length=50)
    duration: int = Field(..., description="Duration in minutes", ge=1)
    impact: Optional[int] = Field(None, ge=-5, le=5)


class EnergyLevelSchema(BaseModel):
    """Energy level schema."""

    time: datetime
    level: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None


class TaskMilestoneSchema(BaseModel):
    """Task milestone schema."""

    time: datetime
    description: str = Field(..., min_length=1, max_length=200)
    completed: bool = False
    completion_time: Optional[datetime] = None


class EnvironmentalFactorsSchema(BaseModel):
    """Environmental factors schema."""

    noise_level: Optional[int] = Field(None, ge=1, le=10)
    lighting: Optional[int] = Field(None, ge=1, le=10)
    temperature: Optional[float] = None
    location: Optional[str] = None
    social_context: Optional[str] = None
    distractions: Optional[List[str]] = None


class HyperfocusSessionSchema(BaseModel):
    """Hyperfocus session base schema."""

    # Basic session info
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=1)
    status: SessionStatus = Field(default=SessionStatus.SCHEDULED)

    # Task and focus details
    task_type: HyperfocusTaskType = Field(default=HyperfocusTaskType.OTHER)
    purpose: str = Field(..., min_length=1, max_length=255)
    focus_area: str = Field(..., min_length=1, max_length=100)

    # Environment and conditions
    environment: Optional[str] = Field(None, max_length=100)
    tools_used: Optional[List[str]] = None
    environmental_factors: Optional[EnvironmentalFactorsSchema] = None
    triggers: Optional[List[str]] = None
    conditions: Optional[Dict[str, Any]] = None

    # Performance metrics
    productivity_score: Optional[int] = Field(None, ge=0, le=100)
    focus_level: Optional[int] = Field(None, ge=1, le=10)
    quality_score: Optional[float] = Field(None, ge=0, le=1)
    completion_rate: Optional[float] = Field(None, ge=0, le=1)

    # Break patterns
    breaks: Optional[List[BreakSchema]] = None
    total_break_time: Optional[int] = Field(None, ge=0)
    break_frequency: Optional[float] = Field(None, ge=0)

    # Additional tracking
    interruptions: Optional[List[InterruptionSchema]] = None
    energy_levels: Optional[List[EnergyLevelSchema]] = None
    task_milestones: Optional[List[TaskMilestoneSchema]] = None
    notes: Optional[str] = None


class HyperfocusSessionCreateSchema(HyperfocusSessionSchema):
    """Hyperfocus session create schema."""

    task_id: Optional[UUID] = None


class HyperfocusSessionUpdateSchema(HyperfocusSessionSchema):
    """Hyperfocus session update schema."""

    pass


class HyperfocusSessionResponseSchema(HyperfocusSessionSchema):
    """Hyperfocus session response schema."""

    id: UUID
    user_id: UUID
    task_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class HyperfocusStatsSchema(BaseModel):
    """Hyperfocus stats schema."""

    total_sessions: int
    total_duration: int  # in minutes
    average_duration: float  # in minutes
    average_productivity: float
    average_focus: float
    average_quality: float
    completion_rate: float
    most_productive_times: List[Dict[str, Any]]
    optimal_session_length: Optional[int]  # in minutes
    optimal_break_patterns: List[Dict[str, Any]]
    common_triggers: List[str]
    effective_environments: List[Dict[str, Any]]
    task_type_distribution: Dict[TaskTypeSchema, int]
    interruption_patterns: List[Dict[str, Any]]
    updated_at: datetime


class HyperfocusTrendsSchema(BaseModel):
    """Hyperfocus trends schema."""

    productivity_trends: List[Dict[str, Any]]
    focus_trends: List[Dict[str, Any]]
    quality_trends: List[Dict[str, Any]]
    duration_trends: List[Dict[str, Any]]
    break_pattern_trends: List[Dict[str, Any]]
    energy_level_trends: List[Dict[str, Any]]
    period_start: datetime
    period_end: datetime
    updated_at: datetime


class OptimalConditionsSchema(BaseModel):
    """Optimal conditions schema."""

    time_of_day: List[str]
    environment: EnvironmentalFactorsSchema
    session_duration: int  # in minutes
    break_pattern: Dict[str, Any]
    tools: List[str]
    task_types: List[TaskTypeSchema]
    confidence_score: float = Field(..., ge=0, le=1)


class HyperfocusSchema(BaseModel):
    """Base schema for hyperfocus sessions."""

    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15)
    session_type: SessionType = Field(default=SessionType.ONE_ON_ONE)
    status: SessionStatus = Field(default=SessionStatus.SCHEDULED)
    activity_type: ActivityType = Field(default=ActivityType.WORK)
    energy_level: Optional[EnergyLevel] = None
    task_description: Optional[str] = Field(None, max_length=1000)
    goals: Optional[List[str]] = None
    is_virtual: bool = True
    notes: Optional[str] = Field(None, max_length=1000)
    meta_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("end_time")
    def validate_end_time(cls, v: datetime, info: ValidationInfo) -> datetime:
        """Validate end time is after start time."""
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("End time must be after start time")
        return v

    model_config = ConfigDict(from_attributes=True)


class HyperfocusSessionCreate(BaseModel):
    """Schema for creating a hyperfocus session."""

    user_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15)
    session_type: SessionType = Field(default=SessionType.ONE_ON_ONE)
    status: SessionStatus = Field(default=SessionStatus.SCHEDULED)
    activity_type: ActivityType = Field(default=ActivityType.WORK)
    energy_level: Optional[EnergyLevel] = None
    task_description: Optional[str] = Field(None, max_length=1000)
    goals: Optional[List[str]] = None
    is_virtual: bool = True
    notes: Optional[str] = Field(None, max_length=1000)
    meta_data: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class HyperfocusSessionUpdate(BaseModel):
    """Schema for updating a hyperfocus session."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15)
    status: Optional[SessionStatus] = None
    activity_type: Optional[ActivityType] = None
    energy_level: Optional[EnergyLevel] = None
    task_description: Optional[str] = Field(None, max_length=1000)
    goals: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=1000)
    meta_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class HyperfocusSessionResponse(BaseModel):
    """Schema for hyperfocus session response."""

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    session_type: SessionType
    status: SessionStatus
    activity_type: ActivityType
    energy_level: Optional[EnergyLevel] = None
    task_description: Optional[str] = None
    goals: Optional[List[str]] = None
    is_virtual: bool
    notes: Optional[str] = None
    meta_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HyperfocusSessionList(BaseModel):
    """Schema for list of hyperfocus sessions."""

    sessions: List[HyperfocusSessionResponse]
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class HyperfocusStats(BaseModel):
    """Schema for hyperfocus session statistics."""

    total_sessions: int
    completed_sessions: int
    total_focus_time: int
    average_duration: float
    completion_rate: float
    most_productive_times: List[int]
    preferred_activity_types: List[str]
    session_stats: Dict[str, int]
    average_focus_rating: float
    average_productivity_rating: float

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "HyperfocusSchema",
    "HyperfocusSessionCreate",
    "HyperfocusSessionUpdate",
    "HyperfocusSessionResponse",
    "HyperfocusSessionList",
    "HyperfocusStats",
]

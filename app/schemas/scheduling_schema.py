"""Scheduling schemas."""
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import Field, BaseModel
from app.models.enums_model import BlockType, BlockPriority
from app.schemas.base_schema import BaseSchema
from app.schemas.shared_components_schema import (
    Break,
    EnvironmentalFactors,
    Interruption,
    SessionAnalytics
)
from enum import Enum

class WorkHours(BaseModel):
    """Work hours schema."""
    
    start_time: time = Field(..., description="Start time of work hours")
    end_time: time = Field(..., description="End time of work hours")
    days_of_week: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4], description="Days of week (0=Monday, 6=Sunday)")

class EnergyLevel(str, Enum):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    productivity_rating: Optional[int] = Field(None, ge=1, le=10)

class TimeBlockInput(BaseSchema):
    """Input schema for time blocks used by energy optimizer."""
    id: str = Field(..., description="Unique identifier for the time block")
    title: str = Field(..., description="Title of the time block")
    start_time: datetime = Field(..., description="Start time of the block")
    end_time: datetime = Field(..., description="End time of the block")
    block_type: BlockType = Field(default=BlockType.TASK, description="Type of block")
    priority: BlockPriority = Field(default=BlockPriority.MEDIUM, description="Priority of the block")
    is_flexible: bool = Field(default=True, description="Whether the block can be moved")
    energy_required: Optional[int] = Field(None, ge=1, le=10, description="Energy level required")
    focus_required: Optional[int] = Field(None, ge=1, le=10, description="Focus level required")
    user_id: Optional[str] = Field(None, description="ID of the user")

class EnergySchedulingPattern(BaseSchema):
    """Energy pattern model for schedule optimization."""
    time_of_day: time
    average_energy: int = Field(..., ge=1, le=10)
    average_focus: int = Field(..., ge=1, le=10)
    common_activities: List[str] = Field(default_factory=list)
    effective_breaks: List[Break] = Field(default_factory=list)
    optimal_recovery_activities: List[str] = Field(default_factory=list)
    environmental_preferences: Optional[EnvironmentalFactors] = None
    peak_hours: List[int] = Field(default_factory=list, description="Hours of the day with peak energy levels")
    trough_hours: List[int] = Field(default_factory=list, description="Hours of the day with low energy levels")
    hourly_energy_levels: Dict[int, float] = Field(default_factory=dict, description="Energy levels by hour")

class SchedulePreferences(BaseSchema):
    """Schedule preferences model."""
    preferred_start_time: time = Field(default=time(9, 0))
    preferred_end_time: time = Field(default=time(17, 0))
    preferred_break_duration: int = Field(default=15, ge=5)  # minutes
    min_break_interval: int = Field(default=90, ge=30)  # minutes
    max_focus_duration: int = Field(default=120, ge=30)  # minutes
    energy_patterns: List[EnergySchedulingPattern] = Field(default_factory=list)
    preferred_task_order: Optional[List[BlockType]] = None
    location_preferences: Optional[Dict[str, List[str]]] = None
    environmental_preferences: Optional[EnvironmentalFactors] = None

class ScheduleBlock(BaseSchema):
    """Schedule block model."""
    start_time: datetime
    end_time: datetime
    block_type: BlockType
    priority: BlockPriority = Field(default=BlockPriority.MEDIUM)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = None
    is_flexible: bool = True
    buffer_before: Optional[int] = Field(None, ge=0)  # minutes
    buffer_after: Optional[int] = Field(None, ge=0)  # minutes
    energy_requirement: Optional[int] = Field(None, ge=1, le=10)
    focus_requirement: Optional[int] = Field(None, ge=1, le=10)
    breaks: Optional[List[Break]] = None
    environmental_requirements: Optional[EnvironmentalFactors] = None
    
    # Performance tracking
    analytics: Optional[SessionAnalytics] = None
    interruptions: Optional[List[Interruption]] = None
    
    # References
    task_id: Optional[UUID] = None
    calendar_event_id: Optional[UUID] = None
    
    meta_data: Optional[Dict[str, Any]] = None

class ScheduleOptimizationRequest(BaseSchema):
    """Schedule optimization request model."""
    start_date: datetime
    end_date: datetime
    blocks: List[ScheduleBlock]
    preferences: SchedulePreferences
    existing_commitments: Optional[List[ScheduleBlock]] = None
    optimization_goals: Optional[Dict[str, float]] = None  # weights for different optimization criteria

class OptimizedSchedule(BaseSchema):
    """Optimized schedule model."""
    blocks: List[ScheduleBlock]
    score: float = Field(..., ge=0, le=1)
    energy_distribution: Dict[str, float]
    break_distribution: List[Break]
    estimated_effectiveness: float = Field(..., ge=0, le=1)
    potential_conflicts: List[Dict[str, Any]]
    alternative_slots: Dict[str, List[Dict[str, Any]]]
    meta_data: Optional[Dict[str, Any]] = None

class ScheduleAnalytics(BaseSchema):
    """Schedule analytics model."""
    total_focus_time: int  # minutes
    total_break_time: int  # minutes
    energy_utilization: float = Field(..., ge=0, le=1)
    break_adherence: float = Field(..., ge=0, le=1)
    schedule_adherence: float = Field(..., ge=0, le=1)
    productivity_score: float = Field(..., ge=0, le=1)
    block_distribution: Dict[BlockType, int]
    energy_patterns: List[EnergySchedulingPattern]
    optimal_schedules: List[Dict[str, Any]]
    improvement_suggestions: List[str]
    period_start: datetime
    period_end: datetime
    meta_data: Optional[Dict[str, Any]] = None

class ScheduleSuggestion(BaseSchema):
    """Schedule suggestion model."""
    blocks: List[ScheduleBlock]
    score: float = Field(..., ge=0, le=1)
    reason: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class TimeBlockBaseSchema(BaseSchema):
    """Base schema for time blocks."""
    start_time: datetime
    end_time: datetime
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    block_type: BlockType = Field(default=BlockType.TASK)
    priority: BlockPriority = Field(default=BlockPriority.MEDIUM)
    is_flexible: bool = Field(default=True)
    energy_required: Optional[int] = Field(None, ge=1, le=10)
    location: Optional[str] = None

class SchedulingRequest(BaseSchema):
    """Schema for scheduling request."""
    start_date: datetime
    end_date: datetime
    blocks: List[TimeBlockBaseSchema]
    preferences: Optional[SchedulePreferences] = None
    existing_commitments: Optional[List[TimeBlockBaseSchema]] = None
    optimization_goals: Optional[Dict[str, float]] = None

class SchedulingSuggestion(BaseSchema):
    """Schema for scheduling suggestions."""
    suggested_blocks: List[TimeBlockBaseSchema]
    score: float = Field(..., ge=0, le=1)
    reason: Optional[str] = None
    alternative_slots: Optional[Dict[str, List[datetime]]] = None
    energy_distribution: Optional[Dict[str, float]] = None
    meta_data: Optional[Dict[str, Any]] = None

class ScheduleResponseSchema(BaseSchema):
    """Schema for schedule response."""
    blocks: List[ScheduleBlock]
    total_focus_time: int = Field(..., description="Total focus time in minutes")
    total_breaks: int = Field(..., description="Total number of breaks")
    meta_data: Optional[Dict[str, Any]] = None

class CircadianCalendarOptimizationRequest(BaseSchema):
    """Schema for circadian calendar optimization request."""
    start_date: datetime
    end_date: datetime
    only_flexible_events: bool = True

class CircadianOptimizationResult(BaseSchema):
    """Schema for single circadian optimization result."""
    event_id: UUID
    title: str
    original_start: datetime
    original_end: datetime
    suggested_start: datetime
    suggested_end: datetime
    time_difference_minutes: int
    suitability_score: float
    cognitive_category: str
    energy_level: float

class CircadianCalendarOptimizationResponse(BaseSchema):
    """Schema for circadian calendar optimization response."""
    optimized_schedule: List[CircadianOptimizationResult]
    energy_curve: List[Dict[str, Any]]
    events_analyzed: int
    events_optimized: int
    message: str

class ApplyCircadianOptimizationRequest(BaseSchema):
    """Schema for applying circadian optimizations."""
    optimization_results: List[CircadianOptimizationResult]

class ApplyCircadianOptimizationResponse(BaseSchema):
    """Schema for the response after applying circadian optimizations."""
    success: bool
    message: str
    applied_count: int
    skipped_count: int
    errors: List[str]
    total_errors: int

__all__ = [
    "EnergySchedulingPattern",
    "SchedulePreferences",
    "ScheduleBlock",
    "ScheduleOptimizationRequest",
    "OptimizedSchedule",
    "ScheduleAnalytics",
    "ScheduleSuggestion",
    "TimeBlockBaseSchema",
    "SchedulingRequest",
    "SchedulingSuggestion",
    "ScheduleResponseSchema",
    "WorkHours",
    "TimeBlockInput",
    "CircadianCalendarOptimizationRequest",
    "CircadianOptimizationResult",
    "CircadianCalendarOptimizationResponse",
    "ApplyCircadianOptimizationRequest",
    "ApplyCircadianOptimizationResponse"
]

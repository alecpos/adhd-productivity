# Generated from mindfulness_model.py

"""Mindfulness schemas for meditation and focus exercises."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import Field, ConfigDict, field_validator

from app.schemas.base_schema import BaseSchema


class MindfulnessSessionBaseSchema(BaseSchema):
    """Base schema for mindfulness sessions."""
    
    user_id: UUID
    session_type: str = Field(..., description="Type of mindfulness session (meditation, breathing, etc.)")
    duration: int = Field(..., ge=1, description="Duration in minutes")
    focus_level: Optional[int] = Field(None, ge=1, le=10, description="Self-reported focus level")
    mood_before: Optional[int] = Field(None, ge=1, le=10, description="Mood before session")
    mood_after: Optional[int] = Field(None, ge=1, le=10, description="Mood after session")
    notes: Optional[str] = Field(None, description="Session notes or observations")
    techniques_used: Optional[List[str]] = Field(default_factory=list, description="Mindfulness techniques used")

    @field_validator("focus_level", "mood_before", "mood_after")
    def validate_ratings(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 10:
            raise ValueError("Rating must be between 1 and 10")
        return v


class MindfulnessSessionCreateSchema(MindfulnessSessionBaseSchema):
    """Schema for creating a new mindfulness session."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the session started")


class MindfulnessSessionResponseSchema(MindfulnessSessionBaseSchema):
    """Schema for mindfulness session response."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = Field(None, description="When the session was completed")
    effectiveness_score: Optional[float] = Field(None, description="Calculated effectiveness score")


class MindfulnessSuggestionSchema(BaseSchema):
    """Schema for mindfulness break suggestions."""
    
    suggestion_type: str = Field(..., description="Type of mindfulness activity")
    title: str = Field(..., description="Title of the suggestion")
    description: str = Field(..., description="Detailed description of the activity")
    duration: int = Field(..., ge=1, description="Recommended duration in minutes")
    benefits: List[str] = Field(..., description="List of potential benefits")
    techniques: List[str] = Field(..., description="List of techniques to use")
    difficulty_level: str = Field(..., description="Difficulty level of the activity")
    energy_required: str = Field(..., description="Energy level required for the activity")
    recommended_time: Optional[str] = Field(None, description="Best time to do this activity")
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class MindfulnessStatsSchema(BaseSchema):
    """Schema for mindfulness statistics."""
    
    user_id: UUID
    total_sessions: int = Field(..., description="Total number of sessions")
    total_minutes: int = Field(..., description="Total minutes spent in mindfulness")
    average_duration: float = Field(..., description="Average session duration")
    favorite_techniques: List[str] = Field(..., description="Most used techniques")
    average_focus_improvement: Optional[float] = Field(None, description="Average improvement in focus")
    average_mood_improvement: Optional[float] = Field(None, description="Average improvement in mood")
    streak_days: Optional[int] = Field(None, description="Current streak of consecutive days")
    last_session: Optional[datetime] = Field(None, description="Date of last session")


__all__ = [
    "MindfulnessSessionBaseSchema",
    "MindfulnessSessionCreateSchema",
    "MindfulnessSessionResponseSchema",
    "MindfulnessSuggestionSchema",
    "MindfulnessStatsSchema"
]

"""Shared component schemas used across multiple modules."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base_schema import BaseSchema


class Break(BaseSchema):
    """Break model used across multiple schemas."""

    start_time: datetime
    end_time: Optional[datetime] = None
    duration: int = Field(..., description="Duration in minutes", ge=1)
    type: str = Field(..., min_length=1, max_length=50)
    effectiveness: Optional[int] = Field(None, ge=1, le=10)


class EnvironmentalFactors(BaseSchema):
    """Environmental factors model used across multiple schemas."""

    noise_level: Optional[int] = Field(None, ge=1, le=10)
    lighting: Optional[int] = Field(None, ge=1, le=10)
    temperature: Optional[float] = None
    location: Optional[str] = None
    social_context: Optional[str] = None
    distractions: Optional[List[str]] = None


class Interruption(BaseSchema):
    """Interruption model used across multiple schemas."""

    time: datetime
    type: str = Field(..., min_length=1, max_length=50)
    duration: int = Field(..., description="Duration in minutes", ge=1)
    impact: Optional[int] = Field(None, ge=-5, le=5)


class SessionAnalytics(BaseSchema):
    """Session analytics model used across multiple schemas."""

    # Focus and productivity metrics
    focus_scores: List[Dict[str, float]]
    productivity_score: float = Field(..., ge=0, le=1)
    effectiveness_score: float = Field(..., ge=0, le=1)
    completion_rate: float = Field(..., ge=0, le=1)

    # Energy and mental state
    energy_levels: List[Dict[str, Any]]
    average_energy: float = Field(..., ge=1, le=10)
    average_focus: float = Field(..., ge=1, le=10)
    mental_state_scores: Optional[List[Dict[str, Any]]] = None

    # Time tracking
    total_focus_time: int = Field(..., description="Total focus time in minutes", ge=0)
    total_break_time: int = Field(..., description="Total break time in minutes", ge=0)
    actual_duration: Optional[int] = Field(None, description="Actual duration in minutes", ge=0)
    estimated_duration: Optional[int] = Field(
        None, description="Estimated duration in minutes", ge=0
    )
    time_efficiency: Optional[float] = Field(None, ge=0, le=1)

    # Break and interruption analysis
    interruption_count: int = Field(default=0, ge=0)
    break_adherence: float = Field(..., ge=0, le=1)
    interruption_impact: Optional[float] = Field(None, ge=-1, le=0)
    break_effectiveness: Optional[float] = Field(None, ge=0, le=1)

    # Environmental impact
    environment_effectiveness: Optional[float] = Field(None, ge=0, le=1)
    optimal_conditions: Optional[Dict[str, Any]] = None

    # Additional metrics
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = None


__all__ = [
    "Break",
    "EnvironmentalFactors",
    "Interruption",
    "SessionAnalytics",
]

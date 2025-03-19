from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import Field

from app.schemas.base_schema import BaseSchema, TimestampedSchema


class VoiceCommandRequestSchema(BaseSchema):
    """Schema for voice command requests."""

    command_text: str = Field(..., min_length=1)
    user_id: UUID
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    command_type: Optional[str] = Field(None, pattern="^(task|reminder|schedule|query|action)$")
    confidence_score: Optional[float] = Field(None, ge=0, le=1)


class VoiceCommandResponseSchema(TimestampedSchema):
    """Schema for voice command responses."""

    success: bool
    message: str
    data: Dict[str, Any]
    command_type: str
    action_taken: str
    confidence_score: float = Field(..., ge=0, le=1)
    requires_confirmation: bool = False
    alternatives: Optional[List[Dict[str, Any]]] = None


class TaskCreationCommandSchema(BaseSchema):
    """Schema for task creation voice commands."""

    title: str = Field(..., min_length=1)
    due_date: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    estimated_duration: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ReminderCreationCommandSchema(BaseSchema):
    """Schema for reminder creation voice commands."""

    title: str = Field(..., min_length=1)
    reminder_time: datetime
    priority: Optional[int] = Field(None, ge=1, le=4)
    repeat_pattern: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|none)$")
    notes: Optional[str] = None


class VoiceCommandLogSchema(TimestampedSchema):
    """Schema for voice command logging."""

    user_id: UUID
    command_text: str
    command_type: str
    success: bool
    confidence_score: float = Field(..., ge=0, le=1)
    processing_time: float
    action_taken: str
    result: Dict[str, Any]
    error: Optional[str] = None


class VoicePreferencesSchema(BaseSchema):
    """Schema for voice command preferences."""

    language: str = Field(..., pattern="^[a-z]{2}-[A-Z]{2}$")
    voice_speed: float = Field(1.0, ge=0.5, le=2.0)
    confirmation_required: bool = True
    wake_word: Optional[str] = None
    custom_commands: Optional[Dict[str, str]] = None
    disabled_commands: List[str] = Field(default_factory=list)


__all__ = [
    "VoiceCommandRequestSchema",
    "VoiceCommandResponseSchema",
    "TaskCreationCommandSchema",
    "ReminderCreationCommandSchema",
    "VoiceCommandLogSchema",
    "VoicePreferencesSchema",
]

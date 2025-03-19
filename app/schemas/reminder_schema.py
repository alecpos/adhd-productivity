"""Reminder schemas module."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReminderType(str, Enum):
    """Reminder type enumeration."""

    TASK = "task"
    EVENT = "event"
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    CUSTOM = "custom"


class ReminderBase(BaseModel):
    """Base schema for reminders."""

    reminder_type: ReminderType = Field(..., description="Type of reminder")
    date: datetime = Field(..., description="When the reminder should trigger")
    notes: Optional[str] = Field(None, description="Additional notes or context")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Priority level (1-5)")

    model_config = ConfigDict(from_attributes=True)


class ReminderCreate(ReminderBase):
    """Schema for creating a new reminder."""

    user_id: UUID = Field(..., description="ID of the user creating the reminder")
    contact_id: Optional[UUID] = Field(None, description="Optional associated contact ID")
    repeat_interval: Optional[str] = Field(None, description="How often to repeat (e.g., 'daily', 'weekly')")


class ReminderUpdate(BaseModel):
    """Schema for updating an existing reminder."""

    reminder_type: Optional[ReminderType] = Field(None, description="Updated reminder type")
    date: Optional[datetime] = Field(None, description="Updated reminder date")
    notes: Optional[str] = Field(None, description="Updated notes")
    completed: Optional[bool] = Field(None, description="Whether the reminder is completed")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Updated priority level")
    contact_id: Optional[UUID] = Field(None, description="Updated associated contact")
    repeat_interval: Optional[str] = Field(None, description="Updated repeat interval")

    model_config = ConfigDict(from_attributes=True)


class ReminderResponse(ReminderBase):
    """Schema for reminder responses."""

    id: UUID = Field(..., description="Unique identifier for the reminder")
    user_id: UUID = Field(..., description="ID of the user who created the reminder")
    contact_id: Optional[UUID] = Field(None, description="Associated contact ID if any")
    completed: bool = Field(default=False, description="Whether the reminder is completed")
    completed_at: Optional[datetime] = Field(None, description="When the reminder was completed")
    created_at: datetime = Field(..., description="When the reminder was created")
    updated_at: datetime = Field(..., description="When the reminder was last updated")
    repeat_interval: Optional[str] = Field(None, description="How often the reminder repeats")
    next_occurrence: Optional[datetime] = Field(None, description="Next scheduled occurrence")

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "ReminderType",
    "ReminderBase",
    "ReminderCreate",
    "ReminderUpdate",
    "ReminderResponse",
]

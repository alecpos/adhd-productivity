# Generated from session_model.py

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BodyDoublingSessionSchema(BaseModel):
    """Schema for body doubling sessions."""

    model_config = ConfigDict(from_attributes=True)


class SessionParticipantSchema(BaseModel):
    """Schema for session participants."""

    model_config = ConfigDict(from_attributes=True)


class StudySessionSchema(BaseModel):
    """Schema for study sessions."""

    model_config = ConfigDict(from_attributes=True)

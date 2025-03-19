"""Interaction schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.enums_model import InteractionType, InteractionOutcome

class InteractionBaseSchema(BaseModel):
    """Base schema for interactions."""
    interaction_type: InteractionType
    outcome: InteractionOutcome = InteractionOutcome.NEUTRAL
    notes: Optional[str] = None
    date: datetime = datetime.utcnow()
    duration_minutes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class InteractionCreateSchema(InteractionBaseSchema):
    """Schema for creating interactions."""
    pass


class InteractionResponseSchema(InteractionBaseSchema):
    """Schema for interaction responses."""
    id: int
    user_id: int
    contact_id: int
    created_at: datetime
    updated_at: datetime

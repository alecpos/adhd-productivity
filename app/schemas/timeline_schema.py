from app.schemas.base_schema import BaseSchema
from pydantic import BaseModel
from pydantic.config import ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class TimelineEventBaseSchema(BaseModel):
    user_id: UUID
    event_type: str  # "task" or "subscription"
    title: str
    due_date: datetime
    description: Optional[str] = None


class TimelineEventCreateSchema(TimelineEventBaseSchema):
    event_id: int  # ID of the linked task or subscription


class TimelineEventResponseSchema(TimelineEventBaseSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class FilteredTimelineResponseSchema(BaseModel):
    timeline: List[TimelineEventResponseSchema]
    message: str

    model_config = ConfigDict(from_attributes=True)

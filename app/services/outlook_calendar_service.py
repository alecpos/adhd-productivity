"""Outlook Calendar integration service."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import BaseService
from app.models.calendar_event_model import CalendarEventModel
from app.schemas.calendar_event_schema import EventResponseSchema, EventCreateSchema


class OutlookCalendarService(
    BaseService[CalendarEventModel, EventResponseSchema, EventCreateSchema]
):
    """Service for Outlook Calendar integration."""

    def __init__(self, db_session: AsyncSession):
        """Initialize Outlook Calendar service."""
        super().__init__(db_session, CalendarEventModel, EventResponseSchema)
        # TODO: Add Outlook Calendar API client initialization

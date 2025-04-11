"""
API endpoints for calendar integration with major platforms.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any

from app.api.deps import get_current_user
from app.models.user_model import UserModel
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional, Union

class CalendarPlatform(str, Enum):
    GOOGLE = "google"
    OUTLOOK = "outlook"
    APPLE = "apple"
    CALDAV = "caldav"
    OTHER = "other"

class EventType(str, Enum):
    TASK = "task"
    MEETING = "meeting"
    REMINDER = "reminder"
    APPOINTMENT = "appointment"
    OTHER = "other"

class ExternalEvent(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    platform: CalendarPlatform
    event_type: EventType = EventType.OTHER

class CalendarSyncResult(BaseModel):
    platform: CalendarPlatform
    events_synced: int
    success: bool
    timestamp: datetime
    error_message: Optional[str] = None

class CalendarIntegrationConfig(BaseModel):
    user_id: str
    platform: CalendarPlatform
    enabled: bool = True
    sync_frequency: int = 15  # minutes

class CalendarIntegrationService:
    async def get_user_integrations(self, user_id: str) -> List[CalendarIntegrationConfig]:
        return [CalendarIntegrationConfig(user_id=user_id, platform=CalendarPlatform.GOOGLE)]

    async def register_integration(self, user_id: str, config: Dict[str, Any]) -> CalendarIntegrationConfig:
        return CalendarIntegrationConfig(user_id=user_id, platform=CalendarPlatform.GOOGLE)

    async def remove_integration(self, user_id: str, platform: CalendarPlatform) -> bool:
        return True

    async def sync_calendars(self, user_id: str, platforms: Optional[List[CalendarPlatform]] = None) -> Dict[CalendarPlatform, int]:
        return {CalendarPlatform.GOOGLE: 5}

    async def get_available_calendars(self, user_id: str, platform: CalendarPlatform) -> List[Dict[str, Any]]:
        return [{"id": "cal1", "name": "Primary Calendar"}]

    async def create_event(self, user_id: str, platform: CalendarPlatform, event_data: Dict[str, Any]) -> ExternalEvent:
        return ExternalEvent(
            id="evt1",
            title="Test Event",
            start_time=datetime.now(),
            platform=platform
        )

    async def update_event(self, user_id: str, platform: CalendarPlatform, event_id: str, event_data: Dict[str, Any]) -> ExternalEvent:
        return ExternalEvent(
            id=event_id,
            title="Updated Event",
            start_time=datetime.now(),
            platform=platform
        )

    async def delete_event(self, user_id: str, platform: CalendarPlatform, event_id: str) -> bool:
        return True

router = APIRouter(
    prefix="/calendars",
    tags=["Calendar Integration", "Integration"]
)
calendar_integration_service = CalendarIntegrationService()


@router.get("/integrations", response_model=List[Dict[str, Any]])
async def get_user_integrations(
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get all calendar integrations for the current user.
    """
    return await calendar_integration_service.get_user_integrations(current_user.id)


@router.post("/integrations", response_model=bool)
async def register_integration(
    config: CalendarIntegrationConfig,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Register a new calendar integration for the current user.
    """
    # Ensure user_id matches current user
    config.user_id = current_user.id
    return await calendar_integration_service.register_integration(config)


@router.delete("/integrations/{platform}/{calendar_id}", response_model=bool)
async def remove_integration(
    platform: CalendarPlatform,
    calendar_id: str,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Remove a calendar integration for the current user.
    """
    return await calendar_integration_service.remove_integration(current_user.id, calendar_id, platform)


@router.get("/sync", response_model=List[CalendarSyncResult])
async def sync_calendars(
    platform: Optional[CalendarPlatform] = None,
    calendar_id: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Synchronize calendars between ADHD Calendar and external services.
    If platform and calendar_id are provided, sync only that calendar, otherwise sync all.
    """
    return await calendar_integration_service.sync_calendars(current_user.id, platform, calendar_id)


@router.get("/calendars", response_model=List[Dict[str, Any]])
async def get_available_calendars(
    platform: CalendarPlatform,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get available calendars from an external platform.
    """
    return await calendar_integration_service.get_available_calendars(current_user.id, platform)


@router.post("/events", response_model=ExternalEvent)
async def create_event_in_external_calendar(
    platform: CalendarPlatform,
    calendar_id: str,
    event_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user),
):
    """
    Create an event directly in an external calendar.
    """
    result = await calendar_integration_service.create_event_in_external_calendar(
        current_user.id, platform, calendar_id, event_data
    )

    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create event")

    return result


@router.put("/events/{platform}/{calendar_id}/{event_id}", response_model=ExternalEvent)
async def update_event_in_external_calendar(
    platform: CalendarPlatform,
    calendar_id: str,
    event_id: str,
    event_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update an event directly in an external calendar.
    """
    result = await calendar_integration_service.update_event_in_external_calendar(
        current_user.id, platform, calendar_id, event_id, event_data
    )

    if result is None:
        raise HTTPException(status_code=400, detail="Failed to update event")

    return result


@router.delete("/events/{platform}/{calendar_id}/{event_id}", response_model=bool)
async def delete_event_in_external_calendar(
    platform: CalendarPlatform,
    calendar_id: str,
    event_id: str,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Delete an event directly from an external calendar.
    """
    return await calendar_integration_service.delete_event_in_external_calendar(
        current_user.id, platform, calendar_id, event_id
    )

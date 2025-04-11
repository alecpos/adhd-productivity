"""
Calendar Integration System with Major Platforms (ADHD-29)

This module provides integration with major calendar platforms, allowing users
to synchronize their schedules across different calendar services.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Set

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CalendarPlatform(str, Enum):
    """Supported calendar platforms for integration."""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    APPLE = "apple"
    CALDAV = "caldav"
    EXCHANGE = "exchange"
    PROTON = "proton"
    ZOHO = "zoho"
    YAHOO = "yahoo"
    CUSTOM = "custom"


class EventType(str, Enum):
    """Types of calendar events."""
    TASK = "task"
    APPOINTMENT = "appointment"
    MEETING = "meeting"
    REMINDER = "reminder"
    DEADLINE = "deadline"
    RECURRING = "recurring"
    ALL_DAY = "all_day"
    CUSTOM = "custom"


class CalendarPermission(str, Enum):
    """Permission levels for calendar access."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    OWNER = "owner"
    NONE = "none"


class CalendarIntegrationConfig(BaseModel):
    """Configuration for a specific calendar integration."""
    user_id: str
    platform: CalendarPlatform
    calendar_id: str  # External calendar identifier
    display_name: str
    color: Optional[str] = None  # Color for events from this calendar
    auth_token: Optional[str] = None
    auth_refresh_token: Optional[str] = None
    auth_expiry: Optional[datetime] = None
    sync_enabled: bool = True
    sync_frequency_minutes: int = 30
    last_sync: Optional[datetime] = None
    sync_events_days_back: int = 30
    sync_events_days_forward: int = 90
    event_types_to_sync: Set[EventType] = Field(default_factory=lambda: set(EventType))
    custom_sync_settings: Dict[str, Any] = Field(default_factory=dict)


class ExternalEvent(BaseModel):
    """Representation of an event from an external calendar platform."""
    event_id: str
    calendar_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_all_day: bool = False
    location: Optional[str] = None
    url: Optional[str] = None
    event_type: EventType = EventType.APPOINTMENT
    recurrence_rule: Optional[str] = None  # iCalendar RRULE format
    attendees: List[Dict[str, str]] = Field(default_factory=list)
    reminders: List[Dict[str, Any]] = Field(default_factory=list)
    color: Optional[str] = None
    transparency: bool = False  # Whether the event blocks time (busy/free)
    organizer: Optional[Dict[str, str]] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    platform: CalendarPlatform
    additional_data: Dict[str, Any] = Field(default_factory=dict)


class CalendarSyncResult(BaseModel):
    """Result of a calendar synchronization operation."""
    success: bool
    platform: CalendarPlatform
    calendar_id: str
    events_imported: int = 0
    events_exported: int = 0
    events_updated: int = 0
    events_deleted: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)


class CalendarIntegration(ABC):
    """Base abstract class for all calendar platform integrations."""

    def __init__(self, config: CalendarIntegrationConfig):
        self.config = config
        self.name = config.platform.value.capitalize()

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the calendar service."""
        pass

    @abstractmethod
    async def fetch_events(
        self, start_date: datetime, end_date: datetime
    ) -> List[ExternalEvent]:
        """Fetch events from the external calendar service."""
        pass

    @abstractmethod
    async def create_event(self, event_data: Dict[str, Any]) -> ExternalEvent:
        """Create a new event in the external calendar service."""
        pass

    @abstractmethod
    async def update_event(self, event_id: str, event_data: Dict[str, Any]) -> ExternalEvent:
        """Update an existing event in the external calendar service."""
        pass

    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Delete an event from the external calendar service."""
        pass

    @abstractmethod
    async def get_calendars(self) -> List[Dict[str, Any]]:
        """Get available calendars from the external service."""
        pass

    async def test_connection(self) -> bool:
        """Test the connection to the external calendar service."""
        try:
            return await self.authenticate()
        except Exception as e:
            logger.error(f"Connection test failed for {self.name}: {str(e)}")
            return False

    async def get_sync_time_range(self) -> tuple[datetime, datetime]:
        """Get the time range for syncing events based on configuration."""
        now = datetime.utcnow()
        start_date = now - timedelta(days=self.config.sync_events_days_back)
        end_date = now + timedelta(days=self.config.sync_events_days_forward)
        return start_date, end_date

    def convert_to_external_format(self, internal_event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert internal event format to the format expected by external API."""
        # This is a base implementation that should be overridden by specific integrations
        return internal_event

    def convert_to_internal_format(self, external_event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert external event format to internal format."""
        # This is a base implementation that should be overridden by specific integrations
        return external_event


class GoogleCalendarIntegration(CalendarIntegration):
    """Integration with Google Calendar."""

    async def authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        try:
            # Check if token needs refresh
            if self.config.auth_expiry and datetime.utcnow() >= self.config.auth_expiry:
                await self._refresh_token()

            # In real implementation, we would verify token with a test API call
            logger.info(f"Successfully authenticated with Google Calendar for user {self.config.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Calendar: {str(e)}")
            return False

    async def _refresh_token(self):
        """Refresh the OAuth token."""
        # In real implementation, we would use refresh token to get a new access token
        # For example:
        # response = requests.post(
        #     "https://oauth2.googleapis.com/token",
        #     data={
        #         "client_id": CLIENT_ID,
        #         "client_secret": CLIENT_SECRET,
        #         "refresh_token": self.config.auth_refresh_token,
        #         "grant_type": "refresh_token",
        #     },
        # )
        # data = response.json()
        # self.config.auth_token = data["access_token"]
        # self.config.auth_expiry = datetime.utcnow() + timedelta(seconds=data["expires_in"])

        # For this example, just simulate token refresh
        logger.info(f"Refreshed Google Calendar token for user {self.config.user_id}")

    async def fetch_events(
        self, start_date: datetime, end_date: datetime
    ) -> List[ExternalEvent]:
        """Fetch events from Google Calendar."""
        try:
            # In real implementation:
            # service = build("calendar", "v3", credentials=credentials)
            # events_result = service.events().list(
            #     calendarId=self.config.calendar_id,
            #     timeMin=start_date.isoformat() + "Z",
            #     timeMax=end_date.isoformat() + "Z",
            #     singleEvents=True,
            #     orderBy="startTime"
            # ).execute()
            # events = events_result.get("items", [])

            # Mock events for example
            mock_events = [
                {
                    "id": "google123",
                    "summary": "Team Meeting",
                    "description": "Weekly team sync",
                    "start": {
                        "dateTime": "2023-06-01T10:00:00-07:00",
                        "timeZone": "America/Los_Angeles",
                    },
                    "end": {
                        "dateTime": "2023-06-01T11:00:00-07:00",
                        "timeZone": "America/Los_Angeles",
                    },
                    "location": "Conference Room B",
                    "attendees": [
                        {"email": "user1@example.com", "displayName": "User One"},
                        {"email": "user2@example.com", "displayName": "User Two"},
                    ],
                    "reminders": {
                        "useDefault": False,
                        "overrides": [{"method": "popup", "minutes": 10}],
                    },
                    "created": "2023-05-20T15:30:00Z",
                    "updated": "2023-05-25T09:15:00Z",
                }
            ]

            # Convert to ExternalEvent objects
            result = []
            for event in mock_events:
                # Parse Google event format to our ExternalEvent model
                start_time = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))

                # Convert attendees format
                attendees = []
                for attendee in event.get("attendees", []):
                    attendees.append({
                        "email": attendee.get("email"),
                        "name": attendee.get("displayName"),
                        "status": attendee.get("responseStatus", "needsAction")
                    })

                # Convert reminders format
                reminders = []
                if "reminders" in event and "overrides" in event["reminders"]:
                    for reminder in event["reminders"]["overrides"]:
                        reminders.append({
                            "method": reminder.get("method"),
                            "minutes_before": reminder.get("minutes")
                        })

                # Create ExternalEvent
                external_event = ExternalEvent(
                    event_id=event["id"],
                    calendar_id=self.config.calendar_id,
                    title=event["summary"],
                    description=event.get("description"),
                    start_time=start_time,
                    end_time=end_time,
                    is_all_day=False,  # would check for 'date' instead of 'dateTime'
                    location=event.get("location"),
                    url=event.get("htmlLink"),
                    event_type=EventType.MEETING,  # determine based on event properties
                    recurrence_rule=event.get("recurrence", [None])[0],
                    attendees=attendees,
                    reminders=reminders,
                    color=event.get("colorId"),
                    transparency=event.get("transparency") == "transparent",
                    created=datetime.fromisoformat(event["created"].replace("Z", "+00:00")) if "created" in event else None,
                    updated=datetime.fromisoformat(event["updated"].replace("Z", "+00:00")) if "updated" in event else None,
                    platform=CalendarPlatform.GOOGLE,
                    additional_data={"etag": event.get("etag")}
                )
                result.append(external_event)

            return result
        except Exception as e:
            logger.error(f"Error fetching Google Calendar events: {str(e)}")
            return []

    async def create_event(self, event_data: Dict[str, Any]) -> ExternalEvent:
        """Create a new event in Google Calendar."""
        try:
            # Convert to Google Calendar API format
            google_event = {
                "summary": event_data["title"],
                "description": event_data.get("description", ""),
                "start": {
                    "dateTime": event_data["start_time"].isoformat(),
                    "timeZone": "UTC",  # would use user's timezone
                },
                "end": {
                    "dateTime": event_data["end_time"].isoformat(),
                    "timeZone": "UTC",  # would use user's timezone
                },
            }

            if event_data.get("location"):
                google_event["location"] = event_data["location"]

            if event_data.get("attendees"):
                google_event["attendees"] = [
                    {"email": a["email"], "displayName": a.get("name")}
                    for a in event_data["attendees"]
                ]

            if event_data.get("reminders"):
                google_event["reminders"] = {
                    "useDefault": False,
                    "overrides": [
                        {"method": r["method"], "minutes": r["minutes_before"]}
                        for r in event_data["reminders"]
                    ],
                }

            # In real implementation:
            # service = build("calendar", "v3", credentials=credentials)
            # created_event = service.events().insert(
            #     calendarId=self.config.calendar_id, body=google_event
            # ).execute()

            # Mock response for this example
            created_event = {
                "id": "new_google_event_123",
                "summary": event_data["title"],
                "description": event_data.get("description", ""),
                "start": {
                    "dateTime": event_data["start_time"].isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": event_data["end_time"].isoformat(),
                    "timeZone": "UTC",
                },
                "created": datetime.utcnow().isoformat() + "Z",
                "updated": datetime.utcnow().isoformat() + "Z",
            }

            # Convert the created event to our format
            return ExternalEvent(
                event_id=created_event["id"],
                calendar_id=self.config.calendar_id,
                title=created_event["summary"],
                description=created_event.get("description"),
                start_time=event_data["start_time"],
                end_time=event_data["end_time"],
                location=event_data.get("location"),
                attendees=event_data.get("attendees", []),
                reminders=event_data.get("reminders", []),
                created=datetime.utcnow(),
                updated=datetime.utcnow(),
                platform=CalendarPlatform.GOOGLE,
            )
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {str(e)}")
            raise

    async def update_event(self, event_id: str, event_data: Dict[str, Any]) -> ExternalEvent:
        """Update an existing event in Google Calendar."""
        try:
            # Convert to Google Calendar API format, similar to create_event
            google_event = {}

            if "title" in event_data:
                google_event["summary"] = event_data["title"]

            if "description" in event_data:
                google_event["description"] = event_data["description"]

            if "start_time" in event_data:
                google_event["start"] = {
                    "dateTime": event_data["start_time"].isoformat(),
                    "timeZone": "UTC",
                }

            if "end_time" in event_data:
                google_event["end"] = {
                    "dateTime": event_data["end_time"].isoformat(),
                    "timeZone": "UTC",
                }

            if "location" in event_data:
                google_event["location"] = event_data["location"]

            if "attendees" in event_data:
                google_event["attendees"] = [
                    {"email": a["email"], "displayName": a.get("name")}
                    for a in event_data["attendees"]
                ]

            if "reminders" in event_data:
                google_event["reminders"] = {
                    "useDefault": False,
                    "overrides": [
                        {"method": r["method"], "minutes": r["minutes_before"]}
                        for r in event_data["reminders"]
                    ],
                }

            # In real implementation:
            # service = build("calendar", "v3", credentials=credentials)
            # updated_event = service.events().update(
            #     calendarId=self.config.calendar_id, eventId=event_id, body=google_event
            # ).execute()

            # Mock response
            # Here we just return the event with updated fields
            return ExternalEvent(
                event_id=event_id,
                calendar_id=self.config.calendar_id,
                title=event_data.get("title", "Updated Event"),
                description=event_data.get("description"),
                start_time=event_data.get("start_time", datetime.utcnow()),
                end_time=event_data.get("end_time", datetime.utcnow() + timedelta(hours=1)),
                location=event_data.get("location"),
                attendees=event_data.get("attendees", []),
                reminders=event_data.get("reminders", []),
                updated=datetime.utcnow(),
                platform=CalendarPlatform.GOOGLE,
            )
        except Exception as e:
            logger.error(f"Error updating Google Calendar event {event_id}: {str(e)}")
            raise

    async def delete_event(self, event_id: str) -> bool:
        """Delete an event from Google Calendar."""
        try:
            # In real implementation:
            # service = build("calendar", "v3", credentials=credentials)
            # service.events().delete(
            #     calendarId=self.config.calendar_id, eventId=event_id
            # ).execute()

            logger.info(f"Deleted Google Calendar event {event_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting Google Calendar event {event_id}: {str(e)}")
            return False

    async def get_calendars(self) -> List[Dict[str, Any]]:
        """Get available calendars from Google Calendar."""
        try:
            # In real implementation:
            # service = build("calendar", "v3", credentials=credentials)
            # calendar_list = service.calendarList().list().execute()
            # return calendar_list.get("items", [])

            # Mock response
            return [
                {
                    "id": "primary",
                    "summary": "Primary Calendar",
                    "backgroundColor": "#4285F4",
                    "primary": True,
                },
                {
                    "id": "work@example.com",
                    "summary": "Work Calendar",
                    "backgroundColor": "#0B8043",
                },
                {
                    "id": "family@example.com",
                    "summary": "Family Calendar",
                    "backgroundColor": "#8E24AA",
                },
            ]
        except Exception as e:
            logger.error(f"Error fetching Google Calendars: {str(e)}")
            return []


class CalendarIntegrationService:
    """
    Service for managing calendar integrations with multiple platforms.
    Handles synchronization, conflict resolution, and integration management.
    """

    def __init__(self):
        self.integrations: Dict[str, Dict[str, CalendarIntegration]] = {}
        self._load_integration_classes()

    def _load_integration_classes(self):
        """Load available integration classes."""
        self.integration_classes = {
            CalendarPlatform.GOOGLE: GoogleCalendarIntegration,
            # Add other integrations as they are implemented
            # CalendarPlatform.OUTLOOK: OutlookCalendarIntegration,
            # CalendarPlatform.APPLE: AppleCalendarIntegration,
        }

    async def register_integration(self, config: CalendarIntegrationConfig) -> bool:
        """Register and initialize a new calendar integration for a user."""
        try:
            # Check if we have an implementation for this platform
            if config.platform not in self.integration_classes:
                logger.error(f"No integration available for {config.platform.value}")
                return False

            # Create the integration instance
            integration_class = self.integration_classes[config.platform]
            integration = integration_class(config)

            # Test the connection
            if not await integration.test_connection():
                logger.error(f"Connection test failed for {config.platform.value}")
                return False

            # Store the integration for the user
            user_id = config.user_id
            if user_id not in self.integrations:
                self.integrations[user_id] = {}

            # We use calendar_id as the key to support multiple calendars of the same platform
            integration_key = f"{config.platform.value}:{config.calendar_id}"
            self.integrations[user_id][integration_key] = integration

            logger.info(f"Registered {config.platform.value} integration for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error registering {config.platform.value} integration: {str(e)}")
            return False

    async def get_user_integrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all registered calendar integrations for a user."""
        if user_id not in self.integrations:
            return []

        result = []
        for key, integration in self.integrations[user_id].items():
            result.append({
                "platform": integration.config.platform.value,
                "calendar_id": integration.config.calendar_id,
                "display_name": integration.config.display_name,
                "color": integration.config.color,
                "sync_enabled": integration.config.sync_enabled,
                "last_sync": integration.config.last_sync,
            })

        return result

    async def remove_integration(self, user_id: str, calendar_id: str, platform: CalendarPlatform) -> bool:
        """Remove a calendar integration for a user."""
        if user_id not in self.integrations:
            return False

        integration_key = f"{platform.value}:{calendar_id}"
        if integration_key not in self.integrations[user_id]:
            return False

        del self.integrations[user_id][integration_key]
        if not self.integrations[user_id]:
            del self.integrations[user_id]

        logger.info(f"Removed {platform.value} integration for user {user_id}")
        return True

    async def sync_calendars(
        self, user_id: str, platform: Optional[CalendarPlatform] = None, calendar_id: Optional[str] = None
    ) -> List[CalendarSyncResult]:
        """
        Synchronize calendars between ADHD Calendar and external services.
        If platform and calendar_id are provided, sync only that calendar, otherwise sync all.
        """
        results = []

        if user_id not in self.integrations:
            logger.warning(f"No integrations registered for user {user_id}")
            return results

        # Determine which integrations to sync
        to_sync = []
        if platform and calendar_id:
            integration_key = f"{platform.value}:{calendar_id}"
            if integration_key in self.integrations[user_id]:
                to_sync.append((integration_key, self.integrations[user_id][integration_key]))
        else:
            to_sync = list(self.integrations[user_id].items())

        # Sync each integration
        for key, integration in to_sync:
            if not integration.config.sync_enabled:
                logger.info(f"Skipping disabled integration {key} for user {user_id}")
                continue

            result = await self._sync_single_calendar(user_id, integration)
            results.append(result)

        return results

    async def _sync_single_calendar(
        self, user_id: str, integration: CalendarIntegration
    ) -> CalendarSyncResult:
        """Synchronize a single calendar integration."""
        result = CalendarSyncResult(
            success=False,
            platform=integration.config.platform,
            calendar_id=integration.config.calendar_id
        )

        try:
            # Start with empty success
            result.success = True

            # Get time range for sync
            start_date, end_date = await integration.get_sync_time_range()

            # Fetch events from external calendar
            external_events = await integration.fetch_events(start_date, end_date)

            # In a real implementation, we would:
            # 1. Get existing events from local database
            # 2. Identify events to create, update, or delete
            # 3. Apply changes to local database and external calendar
            # 4. Handle conflicts

            # For this example, we just mock successful sync counts
            result.events_imported = len(external_events)
            result.events_exported = 0
            result.events_updated = 2
            result.events_deleted = 0

            # Update last sync time
            integration.config.last_sync = datetime.utcnow()

            # In a real implementation, we would save the updated config
            # await self._save_integration_config(integration.config)

            logger.info(
                f"Calendar sync completed for {integration.name}: "
                f"imported {result.events_imported}, "
                f"exported {result.events_exported}, "
                f"updated {result.events_updated}, "
                f"deleted {result.events_deleted}"
            )
        except Exception as e:
            error_msg = f"Error syncing with {integration.name}: {str(e)}"
            logger.error(error_msg)
            result.success = False
            result.errors.append(error_msg)

        return result

    async def get_available_calendars(
        self, user_id: str, platform: CalendarPlatform
    ) -> List[Dict[str, Any]]:
        """Get available calendars from an external platform."""
        # Find the first integration of this platform
        for key, integration in self.integrations.get(user_id, {}).items():
            if integration.config.platform == platform:
                return await integration.get_calendars()

        logger.warning(f"No {platform.value} integration found for user {user_id}")
        return []

    async def create_event_in_external_calendar(
        self, user_id: str, platform: CalendarPlatform, calendar_id: str, event_data: Dict[str, Any]
    ) -> Optional[ExternalEvent]:
        """Create an event directly in an external calendar."""
        integration_key = f"{platform.value}:{calendar_id}"
        if user_id not in self.integrations or integration_key not in self.integrations[user_id]:
            logger.warning(f"Integration {integration_key} not found for user {user_id}")
            return None

        integration = self.integrations[user_id][integration_key]
        try:
            return await integration.create_event(event_data)
        except Exception as e:
            logger.error(f"Error creating event in {platform.value}: {str(e)}")
            return None

    async def update_event_in_external_calendar(
        self, user_id: str, platform: CalendarPlatform, calendar_id: str, event_id: str, event_data: Dict[str, Any]
    ) -> Optional[ExternalEvent]:
        """Update an event directly in an external calendar."""
        integration_key = f"{platform.value}:{calendar_id}"
        if user_id not in self.integrations or integration_key not in self.integrations[user_id]:
            logger.warning(f"Integration {integration_key} not found for user {user_id}")
            return None

        integration = self.integrations[user_id][integration_key]
        try:
            return await integration.update_event(event_id, event_data)
        except Exception as e:
            logger.error(f"Error updating event {event_id} in {platform.value}: {str(e)}")
            return None

    async def delete_event_in_external_calendar(
        self, user_id: str, platform: CalendarPlatform, calendar_id: str, event_id: str
    ) -> bool:
        """Delete an event directly from an external calendar."""
        integration_key = f"{platform.value}:{calendar_id}"
        if user_id not in self.integrations or integration_key not in self.integrations[user_id]:
            logger.warning(f"Integration {integration_key} not found for user {user_id}")
            return False

        integration = self.integrations[user_id][integration_key]
        try:
            return await integration.delete_event(event_id)
        except Exception as e:
            logger.error(f"Error deleting event {event_id} in {platform.value}: {str(e)}")
            return False

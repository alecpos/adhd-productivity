"""Google Calendar integration service."""

import os.path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.base_service import BaseService
from app.models.calendar_event_model import CalendarEventModel
from app.schemas.calendar_event_schema import EventResponseSchema, EventCreateSchema
from app.core.config import settings
from app.core.exceptions import IntegrationError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar",  # Full access
    "https://www.googleapis.com/auth/calendar.events",  # Full access to events
]

class GoogleCalendarService(BaseService[CalendarEventModel, EventResponseSchema, EventCreateSchema]):
    """Service for Google Calendar integration."""

    def __init__(self, db_session: AsyncSession):
        """Initialize Google Calendar service."""
        super().__init__(db_session, CalendarEventModel, EventResponseSchema)
        self.service = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Google Calendar API client."""
        try:
            creds = None
            # The file token.json stores the user's access and refresh tokens
            if os.path.exists(settings.GOOGLE_TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(settings.GOOGLE_TOKEN_PATH, SCOPES)
            
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.GOOGLE_CREDENTIALS_PATH, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(settings.GOOGLE_TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())

            self.service = build("calendar", "v3", credentials=creds)
        except Exception as e:
            raise IntegrationError(f"Failed to initialize Google Calendar client: {str(e)}")

    async def get_upcoming_events(self, max_results: int = 10) -> List[dict]:
        """Get upcoming events from Google Calendar."""
        try:
            if not self.service:
                self._initialize_client()

            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            return events_result.get("items", [])
        except HttpError as error:
            raise IntegrationError(f"Failed to fetch Google Calendar events: {str(error)}")

    async def sync_events(self) -> None:
        """Sync events from Google Calendar to local database."""
        try:
            events = await self.get_upcoming_events(max_results=100)
            for event in events:
                # Convert Google Calendar event to our model
                model_data = {
                    "title": event.get("summary", "Untitled Event"),
                    "description": event.get("description", ""),
                    "start_time": event["start"].get("dateTime", event["start"].get("date")),
                    "end_time": event["end"].get("dateTime", event["end"].get("date")),
                    "location": event.get("location", ""),
                    "external_id": event["id"],
                    "source": "google_calendar"
                }
                
                # Check if event already exists
                existing = await self.get_by_external_id(event["id"])
                if existing:
                    await self.update(existing.id, model_data)
                else:
                    await self.create(model_data)
        except Exception as e:
            raise IntegrationError(f"Failed to sync Google Calendar events: {str(e)}")

    async def get_by_external_id(self, external_id: str) -> Optional[CalendarEventModel]:
        """Get event by external ID."""
        result = await self.db_session.execute(
            select(CalendarEventModel).where(CalendarEventModel.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def create_event(self, event_data: dict) -> dict:
        """Create an event in Google Calendar."""
        try:
            if not self.service:
                self._initialize_client()
            
            event = self.service.events().insert(
                calendarId='primary',
                body=event_data
            ).execute()
            return event
        except HttpError as error:
            raise IntegrationError(f"Failed to create Google Calendar event: {str(error)}")

    async def update_event(self, event_id: str, event_data: dict) -> dict:
        """Update an event in Google Calendar."""
        try:
            if not self.service:
                self._initialize_client()
            
            event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event_data
            ).execute()
            return event
        except HttpError as error:
            raise IntegrationError(f"Failed to update Google Calendar event: {str(error)}")

    async def delete_event(self, event_id: str) -> bool:
        """Delete an event from Google Calendar."""
        try:
            if not self.service:
                self._initialize_client()
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
        except HttpError as error:
            raise IntegrationError(f"Failed to delete Google Calendar event: {str(error)}") 
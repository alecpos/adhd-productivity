from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarAPI:
    def __init__(self):
        self.api_version = "v3"
        self.service_name = "calendar"

    def _build_service(self, access_token: str):
        """Build and return Google CalendarModelSchemaSchema service"""
        credentials = Credentials(token=access_token)
        return build(self.service_name, self.api_version, credentials=credentials)

    async def get_events(
        self,
        calendar_id: str,
        start_time: datetime,
        end_time: datetime,
        access_token: str,
    ) -> List[dict]:
        """Get events from Google CalendarModelSchemaSchema"""
        try:
            service = self._build_service(access_token)
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=start_time.isoformat() + "Z",
                    timeMax=end_time.isoformat() + "Z",
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            return [
                {
                    "id": event["id"],
                    "title": event["summary"],
                    "start": datetime.fromisoformat(
                        event["start"].get("dateTime", event["start"].get("date"))
                    ),
                    "end": datetime.fromisoformat(
                        event["end"].get("dateTime", event["end"].get("date"))
                    ),
                    "description": event.get("description", ""),
                }
            ]

        except HttpError as error:
            print(f"Error accessing Google CalendarModelSchemaSchema: {error}")
            return []

    async def create_event(
        calendar_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str],
        access_token: str,
    ) -> Optional[str]:
        """Create an event in Google CalendarModelSchemaSchema"""
        try:
            service = self._build_service(access_token)
            event = {
                "summary": title,
                "description": description or "",
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC",
                },
                "reminders": {"useDefault": True},
            }

            event = service.events().insert(calendarId=calendar_id, body=event).execute()

            return event["id"]

        except HttpError as error:
            print(f"Error creating Google CalendarModelSchemaSchema event: {error}")

    async def update_event(
        calendar_id: str,
        event_id: str,
        title: Optional[str],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        description: Optional[str],
        access_token: str,
    ) -> bool:
        """Update an event in Google CalendarModelSchemaSchema"""
        try:
            service = self._build_service(access_token)

            # Get existing event
            event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

            # Update fields if provided
            if title:
                event["summary"] = title
            if description:
                event["description"] = description
            if start_time:
                event["start"]["dateTime"] = start_time.isoformat()
            if end_time:
                event["end"]["dateTime"] = end_time.isoformat()

            service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

        except HttpError as error:
            print(f"Error updating Google CalendarModelSchemaSchema event: {error}")

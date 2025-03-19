from O365 import Account
from O365.calendar import CalendarModelSchemaSchema


class OutlookCalendarAPI:
    def __init__(self):
        self.scopes = ["calendar_all"]

    def _get_calendar(self, access_token: str) -> CalendarModelSchemaSchema:
        """Get Outlook CalendarModelSchemaSchema instance"""
        account = Account((None, access_token))
        return account.schedule().get_default_calendar()

    async def get_events(
        self,
        calendar_id: str,
        start_time: datetime,
        end_time: datetime,
        access_token: str,
    ) -> List[dict]:
        """Get events from Outlook CalendarModelSchemaSchema"""
        try:
            calendar = self._get_calendar(access_token)
            q = calendar.new_query("start").greater_equal(start_time)
            q.chain("and").on_attribute("end").less_equal(end_time)

            events = calendar.get_events(query=q, include_recurring=True)

            return [
                {
                    "id": event.object_id,
                    "title": event.subject,
                    "start": event.start,
                    "end": event.end,
                    "description": event.body or "",
                }
            ]

        except Exception as error:
            print(f"Error accessing Outlook CalendarModelSchemaSchema: {error}")
            return []

    async def create_event(
        calendar_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str],
        access_token: str,
    ) -> Optional[str]:
        """Create an event in Outlook CalendarModelSchemaSchema"""
        try:
            calendar = self._get_calendar(access_token)

            event = calendar.new_event()
            event.subject = title
            event.start = start_time
            event.end = end_time
            event.body = description or ""
            event.save()

            return event.object_id

        except Exception as error:
            print(f"Error creating Outlook CalendarModelSchemaSchema event: {error}")

    async def update_event(
        calendar_id: str,
        event_id: str,
        title: Optional[str],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        description: Optional[str],
        access_token: str,
    ) -> bool:
        """Update an event in Outlook CalendarModelSchemaSchema"""
        try:
            calendar = self._get_calendar(access_token)
            event = calendar.get_event(event_id)

            if title:
                event.subject = title
            if description:
                event.body = description
            if start_time:
                event.start = start_time
            if end_time:
                event.end = end_time

            event.save()

        except Exception as error:
            print(f"Error updating Outlook CalendarModelSchemaSchema event: {error}")

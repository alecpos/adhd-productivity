class AppleCalendarAPI:
    def __init__(self):
        self.base_url = "https://caldav.icloud.com"

    def _get_client(self, username: str, password: str):
        """Create and return CalDAV client for Apple CalendarModelSchemaSchema"""
        return caldav.DAVClient(url=self.base_url, username=username, password=password)

    async def get_events(
        calendar_id: str,
        start_time: datetime,
        end_time: datetime,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> List[dict]:
        """Get events from Apple CalendarModelSchemaSchema"""
        try:
            client = self._get_client(username, password)
            principal = client.principal()
            calendar = principal.calendar(calendar_id)

            events = calendar.date_search(start=start_time, end=end_time)

            return [
                {
                    "id": event.id,
                    "title": event.instance.vevent.summary.value,
                    "start": event.instance.vevent.dtstart.value,
                    "end": event.instance.vevent.dtend.value,
                    "description": (
                        getattr(event.instance.vevent, "description", {}).value
                        if hasattr(event.instance.vevent, "description")
                        else ""
                    ),
                }
            ]

        except Exception as error:
            print(f"Error accessing Apple CalendarModelSchemaSchema: {error}")
            return []

    async def create_event(
        calendar_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[str]:
        """Create an event in Apple CalendarModelSchemaSchema"""
        try:
            client = self._get_client(username, password)
            principal = client.principal()
            calendar = principal.calendar(calendar_id)

            event = calendar.save_event(
                dtstart=start_time,
                dtend=end_time,
                summary=title,
                description=description or "",
            )

            return event.id

        except Exception as error:
            print(f"Error creating Apple CalendarModelSchemaSchema event: {error}")

    async def update_event(
        calendar_id: str,
        event_id: str,
        title: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> bool:
        """Update an event in Apple CalendarModelSchemaSchema"""
        try:
            client = self._get_client(username, password)
            principal = client.principal()
            calendar = principal.calendar(calendar_id)
            event = calendar.event(event_id)

            if title:
                event.instance.vevent.summary.value = title
            if description:
                if hasattr(event.instance.vevent, "description"):
                    event.instance.vevent.description.value = description
                else:
                    event.instance.vevent.add("description", description)
            if start_time:
                event.instance.vevent.dtstart.value = start_time
            if end_time:
                event.instance.vevent.dtend.value = end_time

            event.save()

        except Exception as error:
            print(f"Error updating Apple CalendarModelSchemaSchema event: {error}")

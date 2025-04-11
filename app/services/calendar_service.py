"""Calendar service module."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.services.google_calendar_service import GoogleCalendarService
from app.services.apple_calendar_service import AppleCalendarService
from app.services.outlook_calendar_service import OutlookCalendarService
from app.services.calendar_sync_service import CalendarSyncService
from app.models.calendar_model import CalendarEventModel
from app.schemas.calendar_schema import (
    CalendarEventSchema,
    CalendarEventCreateSchema,
    CalendarEventUpdateSchema,
)


class CalendarService(
    BaseService[CalendarEventModel, CalendarEventSchema, CalendarEventCreateSchema]
):
    """Service for managing calendar events."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        super().__init__(db, CalendarEventModel, CalendarEventSchema)
        self.google = GoogleCalendarService(db)
        self.apple = AppleCalendarService(db)
        self.outlook = OutlookCalendarService(db)
        self.sync = CalendarSyncService(db)

    async def create_event(
        self, event_data: CalendarEventCreateSchema, user_id: UUID
    ) -> CalendarEventSchema:
        """Create a new calendar event."""
        event_dict = event_data.model_dump()
        event_dict["user_id"] = user_id
        event = await self.create(event_dict)
        return CalendarEventSchema.model_validate(event)

    async def get_events(
        self, user_id: UUID, skip: int = 0, limit: int = 10
    ) -> List[CalendarEventSchema]:
        """Get calendar events for a user."""
        events = await self.get_many_by_field("user_id", user_id)
        return [CalendarEventSchema.model_validate(event) for event in events[skip : skip + limit]]

    async def get_event(self, event_id: str, user_id: UUID) -> Optional[CalendarEventSchema]:
        """Get a specific calendar event."""
        event = await self.get_by_id(UUID(event_id))
        if event and event.user_id == user_id:
            return CalendarEventSchema.model_validate(event)
        return None

    async def update_event(
        self, event_id: str, event_data: CalendarEventUpdateSchema, user_id: UUID
    ) -> Optional[CalendarEventSchema]:
        """Update a calendar event."""
        event = await self.get_event(event_id, user_id)
        if not event:
            return None

        update_dict = event_data.model_dump(exclude_unset=True)
        updated_event = await self.update(UUID(event_id), update_dict)
        return CalendarEventSchema.model_validate(updated_event) if updated_event else None

    async def delete_event(self, event_id: str, user_id: UUID) -> bool:
        """Delete a calendar event."""
        event = await self.get_event(event_id, user_id)
        if not event:
            return False
        return await self.delete(UUID(event_id))

    async def apply_circadian_optimization(
        self, user_id: UUID, optimization_results: List[dict]
    ) -> Dict[str, Any]:
        """Apply circadian optimization results to calendar events.

        This method updates calendar events based on the optimization
        results from the CircadianDQNModel.

        Args:
            user_id: User ID
            optimization_results: List of optimization results with event IDs
                                  and suggested time changes

        Returns:
            Summary of applied changes
        """
        # Counters for tracking changes
        applied_count = 0
        skipped_count = 0
        errors = []
        updated_events = []

        for result in optimization_results:
            try:
                # Get event ID
                event_id = result.get("event_id")
                if not event_id:
                    skipped_count += 1
                    errors.append(f"Missing event ID in optimization result")
                    continue

                # Get the event
                event = await self.get(UUID(event_id))
                if not event or str(event.user_id) != str(user_id):
                    skipped_count += 1
                    errors.append(f"Event {event_id} not found or not owned by user")
                    continue

                # Parse new times
                new_start = datetime.fromisoformat(result.get("suggested_start"))
                new_end = datetime.fromisoformat(result.get("suggested_end"))

                # Apply changes
                event_update = {
                    "start_time": new_start,
                    "end_time": new_end,
                    "meta_data": {
                        **(event.meta_data or {}),
                        "circadian_optimized": True,
                        "optimization_timestamp": datetime.now().isoformat(),
                        "original_start": result.get("original_start"),
                        "original_end": result.get("original_end"),
                        "suitability_score": result.get("suitability_score", 0.5),
                        "cognitive_category": result.get("cognitive_category", "unknown"),
                        "energy_level": result.get("energy_level", 5.0),
                    },
                }

                # Update the event
                updated_event = await self.update(UUID(event_id), event_update)
                applied_count += 1
                updated_events.append(CalendarEventSchema.model_validate(updated_event))

                # TODO: Add sync with external calendar if needed
                # This would involve calling the appropriate calendar service
                # based on the event's calendar type

            except Exception as e:
                skipped_count += 1
                errors.append(f"Error updating event {result.get('event_id')}: {str(e)}")

        return {
            "applied_count": applied_count,
            "skipped_count": skipped_count,
            "errors": errors,
            "updated_events": updated_events,
        }

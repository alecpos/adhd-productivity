"""Calendar routes module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.models.user_model import UserModel
from app.core.security import get_current_user
from app.schemas.calendar_schema import (
    CalendarEventSchema,
    CalendarEventCreateSchema,
    CalendarEventUpdateSchema,
    CalendarEventResponseSchema,
    CalendarEventListResponseSchema
)
from app.services.calendar_service import CalendarService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post("/events", response_model=CalendarEventResponseSchema, status_code=201)
async def create_calendar_event(
    event: CalendarEventCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create a new calendar event."""
    logger.info(f"Creating calendar event for user: {current_user.id}")
    try:
        calendar_service = CalendarService(db)
        created_event = await calendar_service.create_event(event, current_user.id)
        return CalendarEventResponseSchema(
            success=True,
            message="Calendar event created successfully",
            data=created_event
        )
    except Exception as e:
        logger.error(f"Error creating calendar event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/events", response_model=CalendarEventListResponseSchema)
async def list_calendar_events(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List calendar events for the current user."""
    try:
        calendar_service = CalendarService(db)
        events = await calendar_service.get_events(current_user.id, skip, limit)
        return CalendarEventListResponseSchema(
            success=True,
            message="Calendar events retrieved successfully",
            data=events
        )
    except Exception as e:
        logger.error(f"Error listing calendar events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/events/{event_id}", response_model=CalendarEventResponseSchema)
async def get_calendar_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get a specific calendar event."""
    try:
        calendar_service = CalendarService(db)
        event = await calendar_service.get_event(event_id, current_user.id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar event not found"
            )
        return CalendarEventResponseSchema(
            success=True,
            message="Calendar event retrieved successfully",
            data=event
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving calendar event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/events/{event_id}", response_model=CalendarEventResponseSchema)
async def update_calendar_event(
    event_id: str,
    event: CalendarEventUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update a calendar event."""
    try:
        calendar_service = CalendarService(db)
        updated_event = await calendar_service.update_event(event_id, event, current_user.id)
        if not updated_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar event not found"
            )
        return CalendarEventResponseSchema(
            success=True,
            message="Calendar event updated successfully",
            data=updated_event
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating calendar event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Delete a calendar event."""
    try:
        calendar_service = CalendarService(db)
        deleted = await calendar_service.delete_event(event_id, current_user.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar event not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting calendar event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user_schema import UserSchema
from app.services.auth_service import get_current_user
from app.schemas.hyperfocus_schema import (
    HyperfocusSessionCreateSchema,
    HyperfocusSessionResponseSchema,
    HyperfocusSessionUpdate,
    HyperfocusStats
)
from app.services.hyperfocus_service import HyperfocusService
import logging
from fastapi import APIRouter, Depends, HTTPException, Request

logger = logging.getLogger(__name__)
hyperfocus_router = APIRouter(tags=["Hyperfocus"])


@hyperfocus_router.post("/session", response_model=HyperfocusSessionResponseSchema)
async def start_session(
    request: Request,
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new hyperfocus session."""
    try:
        body = await request.json()
        body["user_id"] = str(current_user.id)
        if "focus_area" not in body:
            body["focus_area"] = body.get("purpose", "General Focus")
        session_data = HyperfocusSessionCreateSchema(**body)
        service = HyperfocusService(db)
        session = await service.start_session(session_data.model_dump())
        return session
    except ValueError as e:
        logger.error(f"Validation error starting hyperfocus session: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting hyperfocus session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@hyperfocus_router.post("/session/{session_id}/end", response_model=HyperfocusSessionResponseSchema)
async def end_session(
    session_id: str,
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """End an active hyperfocus session."""
    try:
        service = HyperfocusService(db)
        session = await service.end_session(session_id, current_user.id)
        return session
    except Exception as e:
        logger.error(f"Error ending hyperfocus session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@hyperfocus_router.get("/sessions", response_model=list[HyperfocusSessionResponseSchema])
async def get_user_sessions(
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all hyperfocus sessions for the current user."""
    try:
        service = HyperfocusService(db)
        sessions = await service.get_user_sessions(current_user.id)
        return sessions
    except Exception as e:
        logger.error(f"Error fetching user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@hyperfocus_router.get("/statistics", response_model=HyperfocusStats)
async def get_session_stats(
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get statistics for the current user's hyperfocus sessions."""
    try:
        service = HyperfocusService(db)
        stats = await service.get_session_stats(current_user.id)
        return stats
    except Exception as e:
        logger.error(f"Error fetching session stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@hyperfocus_router.post("/session/{session_id}/interruption")
async def log_interruption(
    session_id: str,
    reason: str,
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log an interruption for an active hyperfocus session."""
    try:
        service = HyperfocusService(db)
        await service.log_interruption(session_id, reason)
        return {"message": "Interruption logged successfully"}
    except Exception as e:
        logger.error(f"Error logging interruption: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@hyperfocus_router.patch("/session/{session_id}", response_model=HyperfocusSessionResponseSchema)
async def update_session(
    session_id: str,
    update_data: HyperfocusSessionUpdate,
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a hyperfocus session."""
    try:
        service = HyperfocusService(db)
        session = await service.update_session(session_id, update_data.model_dump())
        return session
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@hyperfocus_router.get("/statistics", response_model=HyperfocusStats)
async def get_hyperfocus_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    """Get hyperfocus session statistics for the current user."""
    try:
        service = HyperfocusService(db)
        stats = await service.get_session_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

router = hyperfocus_router

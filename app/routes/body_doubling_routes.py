from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.schemas.body_doubling_schema import (
    BodyDoublingSchema,
    CreateBodyDoublingSchema,
    BodyDoublingResponseSchema,
)
from app.services.body_doubling_service import BodyDoublingService

router = APIRouter()


@router.post("/session", response_model=BodyDoublingResponseSchema)
async def create_session(
    session_data: CreateBodyDoublingSchema, db: AsyncSession = Depends(get_db)
):
    """Create a new body-doubling session."""
    try:
        service = BodyDoublingService(db)
        session = await service.create_session(session_data.host_user_id, session_data)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/active")
async def list_active_sessions(db: AsyncSession = Depends(get_db)):
    """Get all active body-doubling sessions."""
    try:
        service = BodyDoublingService(db)
        sessions = await service.get_active_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/join")
async def join_session(session_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Join an existing body-doubling session."""
    try:
        service = BodyDoublingService(db)
        session = await service.join_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/leave")
async def leave_session(session_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Leave a body-doubling session."""
    try:
        service = BodyDoublingService(db)
        session = await service.leave_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/end")
async def end_session(session_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_db)):
    """End a body-doubling session."""
    try:
        service = BodyDoublingService(db)
        session = await service.end_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

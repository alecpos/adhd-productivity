"""Session manager component for body doubling service."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, select, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType
from app.schemas.body_doubling_schema import CreateBodyDoublingSchema
from app.services.body_doubling.body_doubling_types import SessionMetaData
from app.utils.error_handler import handle_service_error


class SessionManager:
    """Manages body doubling sessions."""

    def __init__(self, db_session: AsyncSession):
        """Initialize the session manager.

        Args:
            db_session: The database session
        """
        self.db = db_session

    async def create_session(
        self, session_data: CreateBodyDoublingSchema
    ) -> BodyDoublingSessionModel:
        """Create a new body doubling session."""
        session = BodyDoublingSessionModel(
            user_id=session_data.user_id,
            host_id=session_data.host_id,
            session_type=session_data.session_type,
            status=SessionStatus.ACTIVE,
            start_time=datetime.now(),
            activity_type=session_data.activity_type,
            max_participants=session_data.max_participants or 2,  # Default for one-on-one sessions
            meta_data={
                "participants": [str(session_data.user_id)],
                "join_requests": [],
                "preferences": {},
                "feedback": []
            }
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session_by_id(self, session_id: UUID) -> Optional[BodyDoublingSessionModel]:
        """Get a session by its ID."""
        query = select(BodyDoublingSessionModel).where(BodyDoublingSessionModel.id == session_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_session(self, user_id: UUID) -> Optional[BodyDoublingSessionModel]:
        """Get the active session for a user."""
        query = select(BodyDoublingSessionModel).where(
            and_(
                BodyDoublingSessionModel.user_id == user_id,
                BodyDoublingSessionModel.status == SessionStatus.ACTIVE,
            )
        ).order_by(desc(BodyDoublingSessionModel.created_at))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_sessions(self, user_id: UUID) -> List[BodyDoublingSessionModel]:
        """Get all sessions for a user."""
        query = select(BodyDoublingSessionModel).where(BodyDoublingSessionModel.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_sessions(self) -> List[BodyDoublingSessionModel]:
        """Get all active sessions."""
        query = select(BodyDoublingSessionModel).where(BodyDoublingSessionModel.status == SessionStatus.ACTIVE)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def join_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """Join a session."""
        session = await self.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Session is not active")
        
        # Initialize metadata if it doesn't exist
        if not session.meta_data:
            session.meta_data = {"participants": [], "join_requests": []}
        
        # Create a deep copy of the metadata to avoid reference issues
        updated_meta_data = dict(session.meta_data)
        
        # Initialize participants list if it doesn't exist
        if "participants" not in updated_meta_data:
            updated_meta_data["participants"] = []
        
        # Add the user to the participants list if not already there
        if str(user_id) not in updated_meta_data["participants"]:
            updated_meta_data["participants"].append(str(user_id))
            
            # Update the session's metadata in the database
            # Update the meta_data field
            meta_data_update = update(BodyDoublingSessionModel).where(
                BodyDoublingSessionModel.id == session_id
            ).values(meta_data=updated_meta_data)
            
            await self.db.execute(meta_data_update)
            await self.db.commit()
            
            # Refresh the session to get the updated data
            await self.db.refresh(session)
        
        return session

    async def leave_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """Leave a session."""
        session = await self.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session.meta_data or "participants" not in session.meta_data:
            raise HTTPException(status_code=400, detail="No participants found in session")
        
        if str(user_id) not in session.meta_data["participants"]:
            raise HTTPException(status_code=400, detail="User is not a participant in this session")
        
        # Create a deep copy of the metadata to avoid reference issues
        updated_meta_data = dict(session.meta_data)
        
        # Remove the user from the participants list
        updated_meta_data["participants"].remove(str(user_id))
        
        # Check if we need to update the session status
        new_status = session.status
        # If this is a one-on-one session and the host is leaving, end the session
        if session.session_type == SessionType.ONE_ON_ONE and session.host_id == user_id:
            new_status = SessionStatus.COMPLETED
        
        # Update the session in the database
        from sqlalchemy import update
        
        # Update the status and meta_data fields
        session_update = update(BodyDoublingSessionModel).where(
            BodyDoublingSessionModel.id == session_id
        ).values(
            status=new_status,
            meta_data=updated_meta_data
        )
        
        await self.db.execute(session_update)
        await self.db.commit()
        
        # Refresh the session to get the updated data
        await self.db.refresh(session)
        return session

    async def end_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """End a session."""
        session = await self.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.host_id != user_id:
            raise HTTPException(status_code=403, detail="Only the host can end the session")
        
        # Update the session status in the database
        from sqlalchemy import update
        
        # Update the status field
        status_update = update(BodyDoublingSessionModel).where(
            BodyDoublingSessionModel.id == session_id
        ).values(status=SessionStatus.COMPLETED)
        
        await self.db.execute(status_update)
        await self.db.commit()
        
        # Refresh the session to get the updated status
        await self.db.refresh(session)
        return session

    async def update_preferences(self, session_id: UUID, preferences: Dict[str, Any]) -> BodyDoublingSessionModel:
        """Update session preferences."""
        session = await self.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Initialize meta_data if it doesn't exist
        if session.meta_data is None:
            updated_meta_data = {}
        else:
            # Create a deep copy of the metadata to avoid reference issues
            updated_meta_data = dict(session.meta_data)
        
        # Ensure all required fields exist in meta_data
        if "participants" not in updated_meta_data:
            updated_meta_data["participants"] = [str(session.user_id)]
        if "join_requests" not in updated_meta_data:
            updated_meta_data["join_requests"] = []
        if "preferences" not in updated_meta_data:
            updated_meta_data["preferences"] = {}
        if "feedback" not in updated_meta_data:
            updated_meta_data["feedback"] = []
        
        # Update preferences
        updated_meta_data["preferences"] = preferences
        
        # Update the session's metadata in the database
        from sqlalchemy import update
        
        # Update the meta_data field
        meta_data_update = update(BodyDoublingSessionModel).where(
            BodyDoublingSessionModel.id == session_id
        ).values(meta_data=updated_meta_data)
        
        await self.db.execute(meta_data_update)
        await self.db.commit()
        
        # Refresh the session to get the updated data
        await self.db.refresh(session)
        return session 
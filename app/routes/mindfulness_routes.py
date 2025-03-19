"""Mindfulness routes for meditation and focus exercises."""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.schemas.user_schema import UserSchema
from app.schemas.mindfulness_schema import (
    MindfulnessSessionResponseSchema,
    MindfulnessSessionCreateSchema,
    MindfulnessSuggestionSchema
)
from app.services.mindfulness_service import MindfulnessService
from app.routes.base_routes import BaseRouter
from app.models.mindfulness_model import MindfulnessSessionModel
from app.core.responses import APIResponse


class MindfulnessRouter(BaseRouter[MindfulnessSessionResponseSchema, MindfulnessService, MindfulnessSessionModel]):
    """Router for mindfulness meditation and focus exercises."""

    def __init__(self):
        """Initialize the router with mindfulness routes."""
        super().__init__(
            prefix="/mindfulness",
            tags=["mindfulness"],
            schema_class=MindfulnessSessionResponseSchema,
            service_class=MindfulnessService,
            model_class=MindfulnessSessionModel
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        """Register custom routes for mindfulness endpoints."""

        @self.router.get("/suggestion", response_model=APIResponse[MindfulnessSuggestionSchema])
        async def get_break_suggestion(
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            """Get a personalized mindfulness suggestion."""
            try:
                service = self.service_class(db)
                suggestion = await service.get_suggestion(current_user.id)
                return APIResponse(
                    data=suggestion,
                    message="Mindfulness suggestion retrieved successfully"
                )
            except Exception as e:
                logger.error(f"Error getting mindfulness suggestion: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        @self.router.post("/session", response_model=APIResponse[MindfulnessSessionResponseSchema])
        async def start_session(
            session_data: MindfulnessSessionCreateSchema,
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            """Start a new mindfulness session."""
            try:
                service = self.service_class(db)
                session_data.user_id = current_user.id
                session = await service.create_session(session_data.model_dump())
                return APIResponse(
                    data=MindfulnessSessionResponseSchema.from_orm(session),
                    message="Mindfulness session started successfully"
                )
            except Exception as e:
                logger.error(f"Error starting mindfulness session: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        @self.router.get("/history", response_model=APIResponse[list[MindfulnessSessionResponseSchema]])
        async def get_session_history(
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            """Get mindfulness session history for the current user."""
            try:
                service = self.service_class(db)
                sessions = await service.get_user_sessions(current_user.id)
                return APIResponse(
                    data=[MindfulnessSessionResponseSchema.from_orm(session) for session in sessions],
                    message="Mindfulness session history retrieved successfully"
                )
            except Exception as e:
                logger.error(f"Error getting mindfulness history: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


logger = logging.getLogger(__name__)
router = MindfulnessRouter().router

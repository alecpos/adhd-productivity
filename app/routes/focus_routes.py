"""Focus session routes."""

from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import APIResponse, ErrorResponse
from app.database import get_db
from app.routes.base_routes import BaseRouter
from app.schemas.focus_schema import (
    FocusSessionSchema,
    FocusSessionCreateSchema,
)
from app.services.focus_service import FocusService
from app.utils.error_handler import handle_service_error
from app.models.focus_model import FocusSessionModel


class FocusRouter(BaseRouter[FocusSessionModel, FocusService, FocusSessionCreateSchema]):
    """Router for focus session endpoints."""

    def __init__(self):
        """Initialize the focus router."""
        super().__init__(
            prefix="/focus",
            tags=["focus"],
            schema_class=FocusSessionSchema,
            service_class=FocusService,
            model_class=FocusSessionModel,
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        @self.router.post("/start", response_model=APIResponse[FocusSessionSchema])
        @handle_service_error
        async def start_focus_session(
            data: FocusSessionCreateSchema, db: AsyncSession = Depends(get_db)
        ):
            """Start a new focus session."""
            service = self.service_class(db)
            session = await service.start_session(data)
            return APIResponse(data=session, message="Focus session started successfully")

        @self.router.post("/{id}/end", response_model=APIResponse[FocusSessionSchema])
        @handle_service_error
        async def end_focus_session(
            id: str,
            productivity_score: Optional[int] = None,
            notes: Optional[str] = None,
            db: AsyncSession = Depends(get_db),
        ):
            """End a focus session."""
            service = self.service_class(db)
            session = await service.end_session(id, productivity_score, notes)
            if not session:
                raise HTTPException(
                    status_code=404,
                    detail=ErrorResponse(
                        message="Session not found",
                        code="NOT_FOUND",
                        details={"id": id},
                    ).dict(),
                )
            return APIResponse(data=session, message="Focus session ended successfully")

        @self.router.post("/{id}/pause", response_model=APIResponse[FocusSessionSchema])
        @handle_service_error
        async def pause_focus_session(
            id: str, reason: Optional[str] = None, db: AsyncSession = Depends(get_db)
        ):
            """Pause a focus session."""
            service = self.service_class(db)
            session = await service.pause_session(id, reason)
            if not session:
                raise HTTPException(
                    status_code=404,
                    detail=ErrorResponse(
                        message="Session not found",
                        code="NOT_FOUND",
                        details={"id": id},
                    ).dict(),
                )
            return APIResponse(data=session, message="Focus session paused successfully")

        @self.router.post("/{id}/resume", response_model=APIResponse[FocusSessionSchema])
        @handle_service_error
        async def resume_focus_session(id: str, db: AsyncSession = Depends(get_db)):
            """Resume a paused focus session."""
            service = self.service_class(db)
            session = await service.resume_session(id)
            if not session:
                raise HTTPException(
                    status_code=404,
                    detail=ErrorResponse(
                        message="Session not found",
                        code="NOT_FOUND",
                        details={"id": id},
                    ).dict(),
                )
            return APIResponse(data=session, message="Focus session resumed successfully")

        @self.router.get("/statistics", response_model=APIResponse)
        @handle_service_error
        async def get_focus_statistics(
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            db: AsyncSession = Depends(get_db),
        ):
            """Get focus session statistics."""
            service = self.service_class(db)
            stats = await service.get_statistics(start_date, end_date)
            return APIResponse(data=stats, message="Focus statistics retrieved successfully")


router = FocusRouter().router

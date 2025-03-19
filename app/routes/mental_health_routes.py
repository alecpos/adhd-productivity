"""Mental health routes."""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.schemas.user_schema import UserSchema
from app.schemas.mental_health_schema import (
    MentalHealthLogResponseSchema,
    MentalHealthLogCreateSchema,
    MentalHealthLogUpdateSchema,
    MentalHealthStatsSchema,
    MentalHealthTrendsSchema
)
from app.services.mental_health_service import MentalHealthService
from app.routes.base_routes import BaseRouter
from app.models.mental_health_model import MentalHealthLogModel
from app.core.responses import APIResponse


class MentalHealthRouter(BaseRouter[MentalHealthLogResponseSchema, MentalHealthService, MentalHealthLogCreateSchema]):
    """Router for mental health endpoints."""

    def __init__(self):
        """Initialize the router with mental health routes."""
        super().__init__(
            prefix="/mental-health",
            tags=["mental-health"],
            schema_class=MentalHealthLogResponseSchema,
            service_class=MentalHealthService,
            model_class=MentalHealthLogModel
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        """Register custom routes for mental health endpoints."""

        @self.router.get("/logs", response_model=APIResponse[list[MentalHealthLogResponseSchema]])
        async def get_mental_health_logs(
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            """Get all mental health logs for a user."""
            try:
                service = self.service_class(db)
                logs = await service.get_user_logs(current_user.id)
                return APIResponse(
                    data=[MentalHealthLogResponseSchema.from_orm(log) for log in logs],
                    message="Mental health logs retrieved successfully"
                )
            except Exception as e:
                logger.error(f"Error getting mental health logs: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        @self.router.post("/logs", response_model=APIResponse[MentalHealthLogResponseSchema])
        async def create_mental_health_log(
            log_data: MentalHealthLogCreateSchema,
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            """Create a new mental health log."""
            try:
                service = self.service_class(db)
                log_data.user_id = current_user.id
                log = await service.create_log(**log_data.model_dump())
                return APIResponse(
                    data=MentalHealthLogResponseSchema.from_orm(log),
                    message="Mental health log created successfully"
                )
            except Exception as e:
                logger.error(f"Error creating mental health log: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        @self.router.get("/stats", response_model=APIResponse[MentalHealthStatsSchema])
        async def get_mental_health_stats(
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            """Get mental health statistics for the current user."""
            try:
                service = self.service_class(db)
                stats = await service.get_user_stats(current_user.id)
                return APIResponse(
                    data=MentalHealthStatsSchema(**stats),
                    message="Mental health stats retrieved successfully"
                )
            except Exception as e:
                logger.error(f"Error getting mental health stats: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        @self.router.get("/trends", response_model=APIResponse[MentalHealthTrendsSchema])
        async def get_mental_health_trends(
            current_user: UserSchema = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            """Get mental health trends for the current user."""
            try:
                service = self.service_class(db)
                trends = await service.get_user_trends(current_user.id)
                return APIResponse(
                    data=MentalHealthTrendsSchema(**trends),
                    message="Mental health trends retrieved successfully"
                )
            except Exception as e:
                logger.error(f"Error getting mental health trends: {str(e)}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


router = MentalHealthRouter().router

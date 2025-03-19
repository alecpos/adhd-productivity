"""Time management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Optional


from app.database import get_db
from app.models.time_block_model import TimeBlockModel
from app.models.user_model import UserModel
from app.routes.base_routes import BaseRouter
from app.schemas.time_block_schema import (
    TimeBlockCreate,  # Create schema
    TimeBlockUpdate,  # Update schema
    TimeBlockResponse  # Response schema
)
from app.schemas.time_block_schema import (
    TimePreferences,
    TimeAnalytics,
)

from app.services.time_management_service import TimeManagementService
from app.core.responses import APIResponse, ErrorResponse
from app.utils.decorators import handle_service_error


class TimeManagementRouter(BaseRouter[TimeBlockModel, TimeManagementService, TimeBlockResponse]):
    """Time management router."""

    def __init__(self):
        """Initialize router with service."""
        super().__init__(
            prefix="/time-management",
            tags=["time-management"],
            schema_class=TimeBlockResponse,
            service_class=TimeManagementService,
            model_class=TimeBlockModel
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        @self.router.post("/blocks", response_model=APIResponse[TimeBlockResponse])
        @handle_service_error
        async def create_time_block(
            block: TimeBlockCreate, db: AsyncSession = Depends(get_db)
        ):
            """Create a new time block."""
            service = self.service_class(db)
            time_block = await service.create_block(block)
            return APIResponse(data=time_block, message="Time block created successfully")

        @self.router.get("/blocks/range", response_model=APIResponse[List[TimeBlockResponse]])
        @handle_service_error
        async def get_time_blocks_in_range(
            start_date: datetime, end_date: datetime, db: AsyncSession = Depends(get_db)
        ):
            """Get all time blocks within a date range."""
            service = self.service_class(db)
            blocks = await service.get_blocks_in_range(start_date, end_date)
            return APIResponse(data=blocks, message="Time blocks retrieved successfully")

        @self.router.put("/blocks/{block_id}", response_model=APIResponse[TimeBlockResponse])
        @handle_service_error
        async def update_time_block(
            block_id: str,
            block: TimeBlockUpdate,
            db: AsyncSession = Depends(get_db),
        ):
            """Update a time block."""
            service = self.service_class(db)
            updated_block = await service.update_block(block_id, block)
            if not updated_block:
                raise HTTPException(
                    status_code=404,
                    detail=ErrorResponse(
                        message="Time block not found",
                        code="NOT_FOUND",
                        details={"block_id": block_id},
                    ).dict(),
                )
            return APIResponse(data=updated_block, message="Time block updated successfully")

        @self.router.put("/preferences", response_model=APIResponse[TimePreferences])
        @handle_service_error
        async def update_time_preferences(
            preferences: TimePreferences, db: AsyncSession = Depends(get_db)
        ):
            """Update time management preferences."""
            service = self.service_class(db)
            updated_prefs = await service.update_preferences(preferences)
            return APIResponse(data=updated_prefs, message="Time preferences updated successfully")

        @self.router.get("/analytics", response_model=APIResponse[TimeAnalytics])
        @handle_service_error
        async def get_time_analytics(
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            db: AsyncSession = Depends(get_db),
        ):
            """Get time management analytics."""
            service = self.service_class(db)
            analytics = await service.get_analytics(start_date, end_date)
            return APIResponse(data=analytics, message="Time analytics retrieved successfully")

        @self.router.post("/optimize", response_model=APIResponse[List[TimeBlockResponse]])
        @handle_service_error
        async def optimize_schedule(
            start_date: datetime, end_date: datetime, db: AsyncSession = Depends(get_db)
        ):
            """Optimize time blocks in schedule."""
            service = self.service_class(db)
            optimized_blocks = await service.optimize_schedule(start_date, end_date)
            return APIResponse(data=optimized_blocks, message="Schedule optimized successfully")

        @self.router.get("/suggestions", response_model=APIResponse[List[TimeBlockResponse]])
        @handle_service_error
        async def get_block_suggestions(date: datetime, db: AsyncSession = Depends(get_db)):
            """Get time block suggestions for a specific date."""
            service = self.service_class(db)
            suggestions = await service.get_block_suggestions(date)
            return APIResponse(data=suggestions, message="Block suggestions retrieved successfully")


router = TimeManagementRouter().router

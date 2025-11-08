import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import APIResponse
from app.core.security import get_current_user
from app.database import get_db
from app.models.analytics_model import UserAnalytics
from app.routes.base_routes import BaseRouter
from app.schemas.analytics_schema import (
    AnalyticsResponseSchema,
    AnalyticsSchema,
    UserInsightsResponseSchema,
)
from app.services.analytics_service import AnalyticsService
from app.services.insights_service import UserInsightsService
from app.utils.error_handler import handle_service_error

logger = logging.getLogger(__name__)


async def get_insights_service(
    db: AsyncSession = Depends(get_db),
) -> UserInsightsService:
    """Dependency to get the user insights service."""
    return UserInsightsService(db)


class AnalyticsRouter(
    BaseRouter[AnalyticsSchema, AnalyticsService, UserAnalytics]
):
    def __init__(self):
        super().__init__(
            prefix="/analytics",
            tags=["analytics"],
            schema_class=AnalyticsSchema,
            service_class=AnalyticsService,
            model_class=UserAnalytics,
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        @self.router.get("/user/{user_id}", response_model=AnalyticsResponseSchema)
        @handle_service_error
        async def get_user_analytics(user_id: UUID, db: AsyncSession = Depends(get_db)):
            """Get user analytics including task and focus metrics."""
            service = self.service_class(db)
            analytics = await service.get_user_analytics(user_id)
            if not analytics:
                raise HTTPException(status_code=404, detail="User analytics not found")
            await service.update_task_analytics(user_id)
            await service.update_focus_analytics(user_id)

        @self.router.get("/user/{user_id}/export")
        @handle_service_error
        async def export_user_data(
            user_id: UUID,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            db: AsyncSession = Depends(get_db),
        ):
            """Export all user data including analytics, tasks, and health records."""
            service = self.service_class(db)
            start_date = start_date or datetime.utcnow() - timedelta(days=365)
            end_date = end_date or datetime.utcnow()
            data = await service.export_user_data(user_id, start_date, end_date)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"user_data_export_{timestamp}.json"
            return JSONResponse(
                content=data,
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/json",
                },
            )

        @self.router.get("/productivity", response_model=APIResponse)
        @handle_service_error
        async def get_productivity_metrics(
            start_date: datetime, end_date: datetime, db: AsyncSession = Depends(get_db)
        ):
            """Get productivity metrics for a date range."""
            service = self.service_class(db)
            metrics = await service.get_productivity_metrics(start_date, end_date)
            return APIResponse(data=metrics, message="Productivity metrics retrieved successfully")

        @self.router.get("/focus-patterns", response_model=APIResponse)
        @handle_service_error
        async def get_focus_patterns(
            start_date: datetime, end_date: datetime, db: AsyncSession = Depends(get_db)
        ):
            """Get focus patterns analysis."""
            service = self.service_class(db)
            patterns = await service.get_focus_patterns(start_date, end_date)
            return APIResponse(data=patterns, message="Focus patterns retrieved successfully")

        @self.router.get("/task-completion", response_model=APIResponse)
        @handle_service_error
        async def get_task_completion_metrics(
            start_date: datetime, end_date: datetime, db: AsyncSession = Depends(get_db)
        ):
            """Get task completion metrics."""
            service = self.service_class(db)
            metrics = await service.get_task_completion_metrics(start_date, end_date)
            return APIResponse(
                data=metrics,
                message="Task completion metrics retrieved successfully",
            )

        @self.router.get("/time-distribution", response_model=APIResponse)
        @handle_service_error
        async def get_time_distribution(
            start_date: datetime, end_date: datetime, db: AsyncSession = Depends(get_db)
        ):
            """Get time distribution analysis."""
            service = self.service_class(db)
            distribution = await service.get_time_distribution(start_date, end_date)
            return APIResponse(
                data=distribution,
                message="Time distribution analysis retrieved successfully",
            )

        @self.router.get("/trends", response_model=APIResponse)
        @handle_service_error
        async def get_productivity_trends(
            start_date: datetime,
            end_date: datetime,
            metric_type: Optional[str] = None,
            db: AsyncSession = Depends(get_db),
        ):
            """Get productivity trends analysis."""
            service = self.service_class(db)
            trends = await service.get_productivity_trends(start_date, end_date, metric_type)
            return APIResponse(data=trends, message="Productivity trends retrieved successfully")

        @self.router.get("/user-insights", response_model=UserInsightsResponseSchema)
        async def get_user_insights(
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            current_user=Depends(get_current_user),
            insights_service: UserInsightsService = Depends(get_insights_service),
        ):
            """Get comprehensive insights about the user's patterns and behaviors."""
            try:
                user_id = current_user.id if hasattr(current_user, "id") else current_user
                profile = await insights_service.get_comprehensive_profile(
                    user_id=user_id, start_date=start_date, end_date=end_date
                )
                return UserInsightsResponseSchema(
                    data=profile,
                    message="User insights retrieved successfully",
                )
            except Exception as e:
                logger.error(f"Error getting user insights: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))


router = AnalyticsRouter().router

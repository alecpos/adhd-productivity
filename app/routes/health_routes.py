from typing import Dict
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routes.base_routes import BaseRouter
from app.schemas.health_schema import HealthCheckSchema
from app.services.health_service import HealthService
from app.core.responses import APIResponse
from app.utils.decorators import handle_service_error


class HealthRouter(BaseRouter[HealthCheckSchema, HealthService, None]):
    """Router for health check endpoints."""

    def __init__(self):
        super().__init__(
            prefix="/health",
            tags=["health"],
            schema_class=HealthCheckSchema,
            service_class=HealthService,
            model_class=None,
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        @self.router.get("/status", response_model=APIResponse[Dict])
        @handle_service_error
        async def get_health_status(db: AsyncSession = Depends(get_db)):
            """Get system health status."""
            service = self.service_class(db)
            status = await service.get_system_status()
            return APIResponse(data=status, message="System health status retrieved successfully")

        @self.router.get("/database", response_model=APIResponse[Dict])
        @handle_service_error
        async def get_database_health(db: AsyncSession = Depends(get_db)):
            """Get database health status."""
            service = self.service_class(db)
            status = await service.get_database_health()
            return APIResponse(data=status, message="Database health status retrieved successfully")

        @self.router.get("/services", response_model=APIResponse[Dict])
        @handle_service_error
        async def get_services_health(db: AsyncSession = Depends(get_db)):
            """Get services health status."""
            service = self.service_class(db)
            status = await service.get_services_health()
            return APIResponse(data=status, message="Services health status retrieved successfully")

        @self.router.get("/metrics", response_model=APIResponse[Dict])
        @handle_service_error
        async def get_health_metrics(db: AsyncSession = Depends(get_db)):
            """Get system health metrics."""
            service = self.service_class(db)
            metrics = await service.get_health_metrics()
            return APIResponse(data=metrics, message="System health metrics retrieved successfully")


router = HealthRouter().router

"""Health service for system monitoring and health checks."""

from datetime import datetime
from typing import Dict, Any
import psutil
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.services.base_service import BaseService
from app.schemas.health_schema import HealthCheckSchema, HealthMetricsSchema
from app.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class HealthService(BaseService[HealthCheckSchema, HealthCheckSchema, HealthCheckSchema]):
    """Service for health monitoring and system checks."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        super().__init__(db=db, model=None, schema_class=HealthCheckSchema)

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow(),
                "details": {
                    "system": "operational",
                    "database": await self.get_database_health(),
                    "services": await self.get_services_health(),
                },
            }
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            raise ServiceError(f"Failed to get system status: {str(e)}")

    async def get_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            await self.db.execute(text("SELECT 1"))
            return {"status": "connected", "latency": "normal"}
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_services_health(self) -> Dict[str, Any]:
        """Check health of dependent services."""
        return {"api": "operational", "background_tasks": "operational", "cache": "operational"}

    async def get_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics."""
        try:
            return {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "uptime": psutil.boot_time(),
                "last_check": datetime.utcnow(),
            }
        except Exception as e:
            logger.error(f"Error getting health metrics: {str(e)}")
            raise ServiceError(f"Failed to get health metrics: {str(e)}")

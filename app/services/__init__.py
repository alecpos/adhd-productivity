"""Services initialization module."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.analytics_service import AnalyticsService
    from app.services.auth_service import AuthService
    from app.services.base_service import BaseService

__all__ = ["AnalyticsService", "AuthService", "BaseService"]

"""Health and metadata endpoints."""

from fastapi import APIRouter, Depends

from app1.api.dependencies import get_app_settings
from app1.core.config import Settings

router = APIRouter(tags=["health"], include_in_schema=False)


@router.get("/health", summary="Service health check")
def health(settings: Settings = Depends(get_app_settings)) -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@router.get("/info", summary="Application metadata")
def info(settings: Settings = Depends(get_app_settings)) -> dict[str, str | None]:
    return {
        "project": settings.project_name,
        "environment": settings.environment,
        "vercel_project": settings.vercel_project,
        "vercel_region": settings.vercel_region,
    }


__all__ = ["router"]

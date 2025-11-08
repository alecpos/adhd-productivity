"""API router assembly for the new application."""

from fastapi import APIRouter

from app1.api.routes import health, tasks, users


def create_api_router() -> APIRouter:
    """Compose the FastAPI router tree for the application."""

    router = APIRouter()
    router.include_router(health.router)
    router.include_router(users.router)
    router.include_router(tasks.router)
    return router


__all__ = ["create_api_router"]

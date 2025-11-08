"""ASGI application factory for the Supabase + Vercel stack."""

from __future__ import annotations

from fastapi import FastAPI

from app1.api import create_api_router
from app1.core.config import get_settings
from app1.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    application = FastAPI(title=settings.project_name, version="1.0.0")
    application.include_router(create_api_router(), prefix=settings.api_prefix)
    return application


app = create_app()

__all__ = ["create_app", "app"]

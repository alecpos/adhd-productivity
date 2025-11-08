"""Shared FastAPI dependencies for the new application stack."""

from collections.abc import Generator

from fastapi import Depends
from supabase import Client

from app1.core.config import Settings, get_settings
from app1.infrastructure.supabase_client import get_supabase_client


def get_app_settings() -> Settings:
    """Return application settings instance."""

    return get_settings()


def supabase_client(settings: Settings = Depends(get_app_settings)) -> Generator[Client, None, None]:
    """Yield a Supabase client configured from environment variables."""

    client = get_supabase_client(settings)
    yield client


__all__ = ["get_app_settings", "supabase_client"]

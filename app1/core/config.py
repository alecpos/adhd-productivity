"""Application settings for the rebuilt architecture."""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration container for the new application stack."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "preview", "production"] = Field(
        default="development",
        description="Deployment environment used for feature flags and logging.",
    )
    api_prefix: str = Field(default="/api", description="Root prefix for API routes.")
    project_name: str = Field(default="ADHD Productivity App", description="Human friendly name.")

    # Supabase configuration
    supabase_url: str = Field(..., alias="SUPABASE_URL", description="Supabase project URL")
    supabase_service_role_key: Optional[str] = Field(
        None,
        alias="SUPABASE_SERVICE_ROLE_KEY",
        description="Service role key used for privileged server operations.",
    )
    supabase_anon_key: Optional[str] = Field(
        None,
        alias="SUPABASE_ANON_KEY",
        description="Fallback key used in development when a service key is not provided.",
    )
    supabase_users_table: str = Field(
        default="users",
        description="Table name used to persist user profiles inside Supabase.",
    )
    supabase_tasks_table: str = Field(
        default="tasks",
        description="Table name for productivity tasks within Supabase.",
    )

    # Vercel specific configuration
    vercel_project: Optional[str] = Field(
        None,
        alias="VERCEL_PROJECT",
        description="Optional Vercel project name, used for metadata and logging.",
    )
    vercel_region: Optional[str] = Field(
        None,
        alias="VERCEL_REGION",
        description="Vercel region hint for latency aware operations.",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    return Settings()  # type: ignore[arg-type]


__all__ = ["Settings", "get_settings"]

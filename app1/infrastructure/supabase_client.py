"""Supabase client management for the new application."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from supabase import Client, create_client

from app1.core.config import Settings


@dataclass(slots=True)
class SupabaseClientManager:
    """Factory class that produces configured Supabase client instances."""

    settings: Settings

    @cached_property
    def client(self) -> Client:
        """Instantiate and cache a Supabase client."""

        service_key = self.settings.supabase_service_role_key
        key_to_use: Optional[str] = service_key or self.settings.supabase_anon_key
        if not key_to_use:
            msg = (
                "A Supabase API key is required. Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY."
            )
            raise RuntimeError(msg)

        return create_client(self.settings.supabase_url, key_to_use)


def get_supabase_client(settings: Settings) -> Client:
    """Convenience helper to create a client from the provided settings."""

    return SupabaseClientManager(settings).client


__all__ = ["SupabaseClientManager", "get_supabase_client"]

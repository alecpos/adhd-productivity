"""Logging utilities tailored for the new application architecture."""

import logging
from typing import Optional

from .config import Settings, get_settings


def configure_logging(settings: Optional[Settings] = None) -> None:
    """Configure a sane default logging setup for Vercel deployments."""

    settings = settings or get_settings()
    log_level = logging.INFO if settings.environment == "production" else logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


__all__ = ["configure_logging"]

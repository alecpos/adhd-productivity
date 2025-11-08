"""Entry point used by Vercel serverless deployments."""

from app1.main import app  # noqa: F401

__all__ = ["app"]

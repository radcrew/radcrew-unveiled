"""Application configuration access (re-exports typed settings)."""

from app.core.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]

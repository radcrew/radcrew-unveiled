"""Pydantic settings loaded from environment and ``backend/.env``."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ``app/core/settings.py`` → app → backend
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    PORT: int = Field(default=8787, ge=1)
    FRONTEND_ORIGIN: str = Field(default="http://localhost:8080")

    HUGGINGFACE_API_KEY: str | None = None
    HUGGINGFACE_MODEL: str = Field(default="Qwen/Qwen2.5-1.5B-Instruct")
    HUGGINGFACE_PROVIDER: str = Field(default="hf-inference")
    HUGGINGFACE_EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    HUGGINGFACE_EMBEDDING_PROVIDER: str = Field(default="hf-inference")

    GITHUB_KB_REPO_URL: AnyHttpUrl | None = None
    GITHUB_KB_TOKEN: str | None = None
    GITHUB_KB_BRANCH: str | None = None
    GITHUB_KB_PATH: str | None = None
    GITHUB_KB_PRIVATE_REPO: bool = Field(default=False)

    COMPANY_FEEDBACK_EMAIL: str = Field(default="code@radcrew.org")
    WEB3FORMS_ACCESS_KEY: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

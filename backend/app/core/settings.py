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
    FRONTEND_ORIGIN: str = Field(default="https://radcrew.org")
    FRONTEND_ORIGINS: str | None = Field(
        default=None,
        description="Optional comma-separated list of browser origins for CORS. If set, replaces FRONTEND_ORIGIN.",
    )

    HF_TOKEN: str | None = None
    HUGGINGFACE_MODEL: str = Field(default="Qwen/Qwen3.5-4B")
    HUGGINGFACE_PROVIDER: str = Field(default="hf-inference")
    HUGGINGFACE_EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    HUGGINGFACE_EMBEDDING_PROVIDER: str = Field(default="hf-inference")

    GITHUB_REPO_URL: AnyHttpUrl | None = None
    GITHUB_TOKEN: str | None = None
    GITHUB_BRANCH: str | None = None
    GITHUB_PATH: str | None = None
    GITHUB_PRIVATE_REPO: bool = Field(default=False)

    COMPANY_FEEDBACK_EMAIL: str = Field(default="code@radcrew.org")
    WEB3FORMS_ACCESS_KEY: str | None = None

    # Deep search: a web-search fallback used only when the static knowledge base
    # can't confidently answer. Inert until WEB_SEARCH_API_KEY is set.
    DEEP_SEARCH_ENABLED: bool = Field(default=True)
    WEB_SEARCH_PROVIDER: str = Field(default="tavily")
    WEB_SEARCH_API_KEY: str | None = None
    WEB_SEARCH_MAX_RESULTS: int = Field(default=5, ge=1, le=20)
    # Trigger deep search when the best KB similarity is below this.
    DEEP_SEARCH_SIMILARITY_THRESHOLD: float = Field(default=0.30, ge=0.0, le=1.0)

    def cors_allow_origins(self) -> list[str]:
        """Origins allowed by CORSMiddleware (exact match, include scheme)."""
        raw = self.FRONTEND_ORIGINS
        if raw and raw.strip():
            return [part.strip() for part in raw.split(",") if part.strip()]
        return [self.FRONTEND_ORIGIN]


@lru_cache
def get_settings() -> Settings:
    return Settings()

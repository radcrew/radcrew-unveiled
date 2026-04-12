"""Pydantic settings loaded from environment and ``backend/.env``."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import AnyHttpUrl, Field, TypeAdapter, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_origin_url = TypeAdapter(AnyHttpUrl)

# ``app/core/settings.py`` → app → backend
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Loaded from environment and optional `.env` (same variable names as Node)."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PORT: int = Field(default=8787, ge=1)
    FRONTEND_ORIGIN: str = Field(default="http://localhost:8080")
    HUGGINGFACE_API_KEY: str | None = None
    # Declared so values from `backend/.env` are loaded; merged into HUGGINGFACE_API_KEY in validator.
    HF_TOKEN: str | None = None
    HUGGINGFACE_MODEL: str = Field(default="Qwen/Qwen2.5-1.5B-Instruct")
    HUGGINGFACE_PROVIDER: str = Field(default="hf-inference")
    HUGGINGFACE_EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    HUGGINGFACE_EMBEDDING_PROVIDER: str = Field(default="hf-inference")
    GITHUB_KB_REPO_URL: AnyHttpUrl | None = None
    GITHUB_KB_TOKEN: str | None = None
    GITHUB_KB_BRANCH: str | None = None
    GITHUB_KB_PATH: str | None = None
    GITHUB_KB_PRIVATE_REPO: bool = Field(default=False)
    # Company feedback via Web3Forms (https://web3forms.com): POST JSON to their API with access_key.
    # When WEB3FORMS_ACCESS_KEY is unset, sending is disabled. Inbox is configured in the Web3Forms dashboard.
    COMPANY_FEEDBACK_EMAIL: str = Field(default="code@radcrew.org")
    WEB3FORMS_ACCESS_KEY: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_api_tokens(cls, data: Any) -> Any:
        """Normalize HF/GitHub token-related env values before field parsing."""
        if not isinstance(data, dict):
            return data
        merged = dict(data)

        api_key = merged.get("HUGGINGFACE_API_KEY")
        if api_key is None or (isinstance(api_key, str) and api_key.strip() == ""):
            token = merged.get("HF_TOKEN") or os.environ.get("HF_TOKEN")
            if token is not None and str(token).strip() != "":
                merged["HUGGINGFACE_API_KEY"] = str(token).strip()

        github_token = merged.get("GITHUB_KB_TOKEN")
        if isinstance(github_token, str):
            stripped = github_token.strip()
            merged["GITHUB_KB_TOKEN"] = stripped if stripped else None
        for key in ("GITHUB_KB_BRANCH", "GITHUB_KB_PATH"):
            value = merged.get(key)
            if isinstance(value, str):
                stripped = value.strip()
                merged[key] = stripped if stripped else None

        wf_key = merged.get("WEB3FORMS_ACCESS_KEY")
        if isinstance(wf_key, str):
            stripped = wf_key.strip()
            merged["WEB3FORMS_ACCESS_KEY"] = stripped if stripped else None

        cf_feedback = merged.get("COMPANY_FEEDBACK_EMAIL")
        if isinstance(cf_feedback, str):
            stripped = cf_feedback.strip()
            merged["COMPANY_FEEDBACK_EMAIL"] = stripped if stripped else "code@radcrew.org"

        return merged

    @field_validator("FRONTEND_ORIGIN")
    @classmethod
    def frontend_origin_must_be_url(cls, value: str) -> str:
        """Match Node `z.string().url()`; keep string form (no trailing-slash coercion)."""
        s = value.strip()
        _origin_url.validate_python(s)
        return s

    @field_validator("HUGGINGFACE_API_KEY", mode="before")
    @classmethod
    def huggingface_api_key_empty_to_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return value

    @field_validator("GITHUB_KB_REPO_URL", mode="before")
    @classmethod
    def github_kb_repo_url_empty_to_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return value

    @model_validator(mode="after")
    def validate_github_kb_settings(self) -> Settings:
        """Require token when private GitHub repo ingestion is enabled."""
        if self.GITHUB_KB_TOKEN and not self.GITHUB_KB_REPO_URL:
            raise ValueError("GITHUB_KB_REPO_URL is required when GITHUB_KB_TOKEN is set.")
        if self.GITHUB_KB_REPO_URL and self.GITHUB_KB_PRIVATE_REPO and not self.GITHUB_KB_TOKEN:
            raise ValueError(
                "GITHUB_KB_TOKEN is required when GITHUB_KB_PRIVATE_REPO is true."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Environment configuration (parity with backend/src/config.ts)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import AnyHttpUrl, Field, TypeAdapter, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_origin_url = TypeAdapter(AnyHttpUrl)

# Always load `backend/.env` regardless of process cwd (uvicorn from repo root, IDEs, etc.).
_BACKEND_DIR = Path(__file__).resolve().parent.parent
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
    CONTENTFUL_SPACE_ID: str | None = None
    CONTENTFUL_DELIVERY_TOKEN: str | None = None
    CONTENTFUL_ENVIRONMENT: str = Field(default="master")

    @model_validator(mode="before")
    @classmethod
    def merge_hf_token(cls, data: Any) -> Any:
        """If HUGGINGFACE_API_KEY is unset/empty, use HF_TOKEN (same as Node mergedProcessEnv)."""
        if not isinstance(data, dict):
            return data
        merged = dict(data)
        raw = merged.get("HUGGINGFACE_API_KEY")
        if raw is None or (isinstance(raw, str) and raw.strip() == ""):
            token = merged.get("HF_TOKEN") or os.environ.get("HF_TOKEN")
            if token is not None and str(token).strip() != "":
                merged["HUGGINGFACE_API_KEY"] = str(token).strip()
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


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Request/response models for HTTP API (parity with backend/src/server.ts Zod schemas)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1500)
    history: list[ChatHistoryMessage] | None = Field(default=None, max_length=12)

    @field_validator("message", mode="before")
    @classmethod
    def strip_message(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

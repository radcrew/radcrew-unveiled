from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmbeddingInferenceConfig:
    access_token: str | None = None
    model: str | None = None
    provider: str | None = None

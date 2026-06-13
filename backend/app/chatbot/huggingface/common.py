"""Shared helpers for the HuggingFace inference wrappers."""

from __future__ import annotations

import logging
from typing import Any

from huggingface_hub import InferenceClient

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

DETERMINISTIC_GENERATION_SEED = 42


def safe_get(obj: Any, key: str) -> Any:
    """Read ``key`` from a dict or attribute-style object, returning None if absent."""
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def providers_to_try(provider_policy: str) -> list[str]:
    """Provider order to attempt: the configured one first, then 'auto' as a fallback.

    'auto' on its own needs no fallback (it already lets HF pick a provider).
    """
    if provider_policy == "auto":
        return ["auto"]
    return [provider_policy, "auto"]


def build_inference_client(provider: str) -> InferenceClient:
    """Construct an InferenceClient for the configured chat model and given provider."""
    settings = get_settings()
    return InferenceClient(
        model=settings.HUGGINGFACE_MODEL,
        token=settings.HF_TOKEN,
        provider=provider,
    )  # type: ignore[arg-type]

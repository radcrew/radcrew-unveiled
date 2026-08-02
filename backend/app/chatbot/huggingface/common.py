"""Shared helpers for the HuggingFace inference wrappers."""

from __future__ import annotations

import logging
from typing import Any

from huggingface_hub import InferenceClient

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

DETERMINISTIC_GENERATION_SEED = 42

# Default answer length budget for chat/text generation (the routing and
# confirmation classifiers override this with smaller values).
DEFAULT_MAX_TOKENS = 512

# Decoding settings shared by every inference call so responses are reproducible
# (greedy, fixed seed). Spread into the client call: ``**DETERMINISTIC_DECODING``.
DETERMINISTIC_DECODING = {
    "temperature": 0,
    "top_p": 1,
    "seed": DETERMINISTIC_GENERATION_SEED,
}


def is_retryable_error(err: Exception) -> bool:
    """Whether another attempt could plausibly succeed.

    A depleted account (402), a bad token (401/403), or an unknown model (404)
    answers identically however many times we ask, so retrying only multiplies
    the failed calls against an account that is already out of credit. Anything
    without an HTTP status is a transport error or timeout, which is exactly the
    case retrying exists for.
    """
    status = getattr(getattr(err, "response", None), "status_code", None)
    if status is None:
        return True
    return status == 429 or status >= 500


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

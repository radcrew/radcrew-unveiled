"""Provider-neutral entry points for chat inference.

Which backend runs is decided by whichever credential is configured, via
``Settings.llm_provider()``: ``OPENROUTER_API_KEY`` selects OpenRouter,
otherwise ``HF_TOKEN`` selects Hugging Face. Everything downstream (the RAG
node, the guardrail classifiers, the feedback router) goes through here and
stays provider-blind.

Embeddings are deliberately not part of this. OpenRouter exposes no embeddings
endpoint, so ``knowledge/embeddings.py`` still talks to Hugging Face directly
and degrades to lexical retrieval when HF_TOKEN is absent.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

# Submodule imports (not ``from app.chatbot import openrouter``): this module is
# re-exported by app/chatbot/__init__.py, so reaching back through the parent
# package would resolve against a half-initialised module.
from app.chatbot.huggingface import generate_answer as _hf_generate_answer
from app.chatbot.huggingface.common import DEFAULT_MAX_TOKENS
from app.chatbot.huggingface.structured import complete_json as _hf_complete_json
from app.chatbot.openrouter import generate_answer as _or_generate_answer
from app.chatbot.openrouter.client import complete_json as _or_complete_json
from app.core.settings import get_settings


def active_provider() -> str:
    """Name of the backend that will serve the next call."""
    return get_settings().llm_provider()


def generate_answer(
    system: str,
    user: str,
    history: list[dict[str, str]] | None = None,
) -> Iterator[str]:
    """Stream an answer from the configured backend."""
    if active_provider() == "openrouter":
        return _or_generate_answer(system, user, history)
    return _hf_generate_answer(system, user, history)


def complete_json(
    messages: list[dict[str, str]],
    schema_name: str,
    schema_description: str,
    schema: dict[str, Any],
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Return one schema-constrained JSON completion from the configured backend.

    Raises on transport or provider errors. Both callers treat any failure as
    "could not classify" and fall back to normal routing, so failures here are
    never fatal to a request.
    """
    if active_provider() == "openrouter":
        return _or_complete_json(
            messages, schema_name, schema_description, schema, max_tokens
        )
    return _hf_complete_json(messages, schema_name, schema_description, schema, max_tokens)


__all__ = [
    "active_provider",
    "complete_json",
    "generate_answer",
]

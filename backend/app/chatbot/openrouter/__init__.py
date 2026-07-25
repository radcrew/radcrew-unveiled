"""OpenRouter inference: streaming answers and schema-constrained completions."""

from __future__ import annotations

from collections.abc import Iterator

from app.chatbot.openrouter.client import complete_json, stream_chat_completion


def generate_answer(
    system: str,
    user: str,
    history: list[dict[str, str]] | None = None,
) -> Iterator[str]:
    """Stream an answer for one turn. Mirrors the Hugging Face entry point.

    OpenRouter is uniformly chat-completions, so there is no text-generation
    fallback and no provider ladder to walk: routing between upstream providers
    happens on OpenRouter's side.
    """
    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user})

    return stream_chat_completion(messages)


__all__ = [
    "complete_json",
    "generate_answer",
    "stream_chat_completion",
]

"""Streaming chat-completion wrapper around the HuggingFace InferenceClient."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from app.chatbot.huggingface.common import (
    DEFAULT_MAX_TOKENS,
    DETERMINISTIC_DECODING,
    build_inference_client,
    safe_get,
)


def extract_stream_content(chunk: Any) -> str:
    try:
        choices = safe_get(chunk, "choices")
        first = choices[0] if choices else None
        delta = safe_get(first, "delta")
        content = safe_get(delta, "content")
        return content if isinstance(content, str) else ""
    except Exception:
        return ""


def stream_chat_completion(
    messages: list[dict[str, str]],
    provider: str,
) -> Iterator[str]:
    client = build_inference_client(provider)

    stream = client.chat_completion(
        messages=messages,
        max_tokens=DEFAULT_MAX_TOKENS,
        stream=True,
        **DETERMINISTIC_DECODING,
    )

    for chunk in stream:
        content = extract_stream_content(chunk)
        if content:
            yield content

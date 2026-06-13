"""Streaming text-generation wrapper (fallback for providers without chat support)."""

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
    if isinstance(chunk, str):
        return chunk

    token = safe_get(chunk, "token")
    text = safe_get(token, "text")
    if isinstance(text, str):
        return text

    text = safe_get(chunk, "generated_text")
    if isinstance(text, str):
        return text

    return ""


def _fold_messages_to_prompt(messages: list[dict[str, str]]) -> str:
    """text_generation has no role concept; flatten the turns into one prompt."""
    parts: list[str] = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            parts.append(content)
        elif role == "assistant":
            parts.append(f"Assistant: {content}")
        else:
            parts.append(f"User: {content}")
    parts.append("Assistant:")
    return "\n\n".join(parts)


def stream_text_generation(
    messages: list[dict[str, str]],
    provider: str,
) -> Iterator[str]:
    prompt = _fold_messages_to_prompt(messages)
    client = build_inference_client(provider)

    stream = client.text_generation(
        prompt,
        max_new_tokens=DEFAULT_MAX_TOKENS,
        return_full_text=False,
        do_sample=False,
        stream=True,
        **DETERMINISTIC_DECODING,
    )

    for chunk in stream:
        content = extract_stream_content(chunk)
        if content:
            yield content

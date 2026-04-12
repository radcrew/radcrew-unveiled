"""Hugging Face ``chat_completion`` for feedback intent routing (structured reply)."""

from __future__ import annotations

from typing import Any

from huggingface_hub import InferenceClient
from huggingface_hub.inference._generated.types.chat_completion import (
    ChatCompletionInputResponseFormatJSONObject,
)

from app.chatbot.huggingface.common import DETERMINISTIC_GENERATION_SEED

from .constants import _FEEDBACK_ROUTE_REPLY_SUFFIX


def feedback_route_messages(base: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Append the user instruction that asks for a ``tool_call`` JSON object."""
    return [*base, {"role": "user", "content": _FEEDBACK_ROUTE_REPLY_SUFFIX}]


def feedback_route_completion(
    model: str,
    access_token: str,
    messages: list[dict[str, Any]],
    provider: str,
    use_json_object_format: bool,
) -> Any:
    client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
    params: dict[str, Any] = {
        "messages": messages,
        "stream": False,
        "max_tokens": 512,
        "temperature": 0,
        "top_p": 1,
        "seed": DETERMINISTIC_GENERATION_SEED,
    }
    if use_json_object_format:
        params["response_format"] = ChatCompletionInputResponseFormatJSONObject(type="json_object")
    return client.chat_completion(**params)

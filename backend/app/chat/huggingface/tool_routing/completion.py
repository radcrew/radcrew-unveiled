"""Single-shot Hugging Face ``chat_completion`` calls for feedback routing."""

from __future__ import annotations

from typing import Any

from huggingface_hub import InferenceClient
from huggingface_hub.inference._generated.types.chat_completion import (
    ChatCompletionInputResponseFormatJSONObject,
)

from app.chat.huggingface.common import DETERMINISTIC_GENERATION_SEED

from .constants import _JSON_FALLBACK_SUFFIX, _SEND_FEEDBACK_TOOL


def tool_router_completion(
    model: str,
    access_token: str,
    messages: list[dict[str, Any]],
    provider: str,
) -> Any:
    client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
    return client.chat_completion(
        messages=messages,
        tools=_SEND_FEEDBACK_TOOL,
        tool_choice="auto",
        stream=False,
        max_tokens=512,
        temperature=0,
        top_p=1,
        seed=DETERMINISTIC_GENERATION_SEED,
    )


def json_fallback_messages(base: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [*base, {"role": "user", "content": _JSON_FALLBACK_SUFFIX}]


def json_fallback_completion(
    model: str,
    access_token: str,
    messages: list[dict[str, Any]],
    provider: str,
    *,
    use_json_object_format: bool,
) -> Any:
    client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
    kwargs: dict[str, Any] = {
        "messages": messages,
        "stream": False,
        "max_tokens": 512,
        "temperature": 0,
        "top_p": 1,
        "seed": DETERMINISTIC_GENERATION_SEED,
    }
    if use_json_object_format:
        kwargs["response_format"] = ChatCompletionInputResponseFormatJSONObject(type="json_object")
    return client.chat_completion(**kwargs)

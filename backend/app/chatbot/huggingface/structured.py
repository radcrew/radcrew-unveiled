"""Schema-constrained (non-streaming) completion via the HuggingFace client.

The feedback router and the confirmation classifier both need a parseable JSON
label rather than prose. This is the HuggingFace half of that; the OpenRouter
half lives in ``app.chatbot.openrouter.client.complete_json`` and both are
selected through ``app.chatbot.llm.complete_json``.
"""

from __future__ import annotations

from typing import Any

from huggingface_hub import InferenceClient
from huggingface_hub.inference._generated.types.chat_completion import (
    ChatCompletionInputJSONSchema,
    ChatCompletionInputResponseFormatJSONSchema,
)

from app.chatbot.huggingface.common import DEFAULT_MAX_TOKENS, DETERMINISTIC_DECODING
from app.core.settings import get_settings


def complete_json(
    messages: list[dict[str, str]],
    schema_name: str,
    schema_description: str,
    schema: dict[str, Any],
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Return the raw JSON string the model emitted, or "" when it produced nothing."""
    settings = get_settings()
    client = InferenceClient(
        model=settings.HUGGINGFACE_MODEL,
        token=settings.HF_TOKEN,
        provider=settings.HUGGINGFACE_PROVIDER,
    )  # type: ignore[arg-type]

    response = client.chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        **DETERMINISTIC_DECODING,
        response_format=ChatCompletionInputResponseFormatJSONSchema(
            type="json_schema",
            json_schema=ChatCompletionInputJSONSchema(
                name=schema_name,
                description=schema_description,
                schema=schema,
                strict=True,
            ),
        ),
    )

    return response.choices[0].message.content or ""

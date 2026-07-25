"""OpenRouter chat completions over its OpenAI-compatible REST API.

HTTP goes through ``urllib`` to match the rest of the backend (the GitHub
loader, web search, and feedback submit all do the same) rather than pulling in
an SDK for two endpoints.

Decoding defaults are shared with the Hugging Face path so switching providers
does not silently change answer style. OpenRouter forwards ``seed`` upstream,
but honouring it is model-dependent; ``temperature=0`` is what actually keeps
answers stable.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from collections.abc import Iterator
from typing import Any

from app.chatbot.huggingface.common import DEFAULT_MAX_TOKENS, DETERMINISTIC_DECODING
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT_SECONDS = 60

# Optional attribution headers. OpenRouter uses them for its public rankings;
# they do not affect routing or billing.
_REFERER = "https://radcrew.org"
_TITLE = "RadCrew Unveiled"


def _open(payload: dict[str, Any]):
    """POST to /chat/completions and return the raw response handle."""
    settings = get_settings()
    url = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": _REFERER,
            "X-Title": _TITLE,
        },
        method="POST",
    )
    return urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS)


def _base_payload(messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    return {
        "model": get_settings().OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        **DETERMINISTIC_DECODING,
    }


def _delta_content(chunk: dict[str, Any]) -> str:
    choices = chunk.get("choices") or []
    if not choices:
        return ""
    delta = choices[0].get("delta") or {}
    content = delta.get("content")
    return content if isinstance(content, str) else ""


def stream_chat_completion(
    messages: list[dict[str, str]],
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> Iterator[str]:
    """Yield answer text as it streams back.

    The response is SSE: ``data:`` lines carrying JSON, terminated by
    ``data: [DONE]``. OpenRouter also emits ``: OPENROUTER PROCESSING`` comment
    lines to hold the connection open, which are skipped by the prefix check.
    """
    payload = _base_payload(messages, max_tokens) | {"stream": True}

    with _open(payload) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue

            data = line.removeprefix("data:").strip()
            if data == "[DONE]":
                return

            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                logger.warning("[openrouter] skipping unparseable stream chunk")
                continue

            content = _delta_content(chunk)
            if content:
                yield content


def complete_json(
    messages: list[dict[str, str]],
    schema_name: str,
    schema_description: str,
    schema: dict[str, Any],
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Return one non-streamed completion constrained to a JSON schema.

    Used by the feedback router and confirmation classifier, which need a
    parseable label rather than prose.
    """
    payload = _base_payload(messages, max_tokens) | {
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "description": schema_description,
                "schema": schema,
                "strict": True,
            },
        },
    }

    with _open(payload) as response:
        body = json.loads(response.read().decode("utf-8"))

    choices = body.get("choices") or []
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content") or ""

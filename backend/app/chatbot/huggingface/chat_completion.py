from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from huggingface_hub import InferenceClient
from app.chatbot.huggingface.common import DETERMINISTIC_GENERATION_SEED, safe_get
from app.core.settings import get_settings


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
    prompt: str,
    provider: str,
) -> Iterator[str]:
    settings = get_settings()

    client = InferenceClient(
        model=settings.HUGGINGFACE_MODEL,
        token=settings.HF_TOKEN,
        provider=provider
    )  # type: ignore[arg-type]

    stream = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0,
        top_p=1,
        seed=DETERMINISTIC_GENERATION_SEED,
        stream=True,
    )

    for chunk in stream:
        content = extract_stream_content(chunk)
        if content:
            yield content

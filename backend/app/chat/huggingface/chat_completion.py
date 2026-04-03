from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from huggingface_hub import InferenceClient
from app.chat.huggingface.common import DETERMINISTIC_GENERATION_SEED, safe_get


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
    model: str,
    access_token: str,
    prompt: str,
    provider: str,
) -> Iterator[str]:
    client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
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

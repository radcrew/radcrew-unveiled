from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from huggingface_hub import InferenceClient
from app.chat.huggingface.common import DETERMINISTIC_GENERATION_SEED, safe_get


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


def stream_text_generation(
    model: str,
    access_token: str,
    prompt: str,
    provider: str,
) -> Iterator[str]:
    client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
    stream = client.text_generation(
        prompt,
        max_new_tokens=512,
        return_full_text=False,
        do_sample=False,
        temperature=0,
        top_p=1,
        seed=DETERMINISTIC_GENERATION_SEED,
        stream=True,
    )
    for chunk in stream:
        content = extract_stream_content(chunk)
        if content:
            yield content

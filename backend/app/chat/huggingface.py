"""Hugging Face Inference: chat completion, then text generation (parity with backend/src/chat/huggingface.ts)."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import Any

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HFValidationError, HfHubHTTPError

logger = logging.getLogger(__name__)

DETERMINISTIC_GENERATION_SEED = 42


def _providers_to_try(provider_policy: str) -> list[str]:
    primary = provider_policy
    if primary == "auto":
        return ["auto"]
    return [primary, "auto"]


def _log_hf_error(phase: str, provider: str, err: BaseException) -> None:
    if isinstance(err, HfHubHTTPError):
        resp = err.response
        status = getattr(resp, "status_code", None)
        body: str
        try:
            parsed = resp.json()
            body = json.dumps(parsed) if isinstance(parsed, (dict, list)) else str(parsed)
        except Exception:
            try:
                body = resp.text
            except Exception:
                body = str(err)
        logger.error(
            "[HF %s provider=%s] status=%s body=%s",
            phase,
            provider,
            status,
            body,
        )
    elif isinstance(err, HFValidationError):
        logger.error("[HF %s provider=%s] %s", phase, provider, err)
    else:
        logger.error("[HF %s provider=%s] %s", phase, provider, err)


def _extract_chat_stream_delta(chunk: Any) -> str:
    if isinstance(chunk, dict):
        choices = chunk.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                delta = first.get("delta")
                if isinstance(delta, dict):
                    content = delta.get("content")
                    if isinstance(content, str):
                        return content
    if hasattr(chunk, "choices"):
        try:
            choices = getattr(chunk, "choices")
            if choices:
                first = choices[0]
                delta = getattr(first, "delta", None)
                content = getattr(delta, "content", None)
                return content if isinstance(content, str) else ""
        except Exception:
            return ""
    return ""


def _extract_text_generation_stream_delta(chunk: Any) -> str:
    if isinstance(chunk, str):
        return chunk
    if isinstance(chunk, dict):
        token = chunk.get("token")
        if isinstance(token, dict):
            text = token.get("text")
            if isinstance(text, str):
                return text
        generated_text = chunk.get("generated_text")
        if isinstance(generated_text, str):
            return generated_text
    if hasattr(chunk, "token"):
        token = getattr(chunk, "token", None)
        text = getattr(token, "text", None)
        if isinstance(text, str):
            return text
    if hasattr(chunk, "generated_text"):
        text = getattr(chunk, "generated_text", None)
        if isinstance(text, str):
            return text
    return ""


def generate_answer(
    model: str,
    access_token: str,
    prompt: str,
    provider_policy: str = "hf-inference",
) -> Iterator[str]:
    providers = _providers_to_try(provider_policy)

    for provider in providers:
        try:
            client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
            stream = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0,
                top_p=1,
                seed=DETERMINISTIC_GENERATION_SEED,
                stream=True,
            )
            yielded_any = False
            for chunk in stream:
                delta = _extract_chat_stream_delta(chunk)
                if delta:
                    yielded_any = True
                    yield delta
            if yielded_any:
                return
        except Exception as err:
            if isinstance(err, (HfHubHTTPError, HFValidationError)):
                _log_hf_error("chatCompletionStream", str(provider), err)
            else:
                logger.error("[HF chatCompletionStream provider=%s] %s", provider, err)

    for provider in providers:
        try:
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
            yielded_any = False
            for chunk in stream:
                delta = _extract_text_generation_stream_delta(chunk)
                if delta:
                    yielded_any = True
                    yield delta
            if yielded_any:
                return
        except Exception as err:
            if isinstance(err, (HfHubHTTPError, HFValidationError)):
                _log_hf_error("textGenerationStream", str(provider), err)
            else:
                logger.error("[HF textGenerationStream provider=%s] %s", provider, err)

    raise RuntimeError(
        f'No inference provider could stream model "{model}". Try HUGGINGFACE_PROVIDER=auto, '
        "pick another HUGGINGFACE_MODEL, or enable a provider at "
        "https://huggingface.co/settings/inference-providers",
    )

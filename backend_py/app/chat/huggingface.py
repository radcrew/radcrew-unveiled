"""Hugging Face Inference: chat completion, then text generation (parity with backend/src/chat/huggingface.ts)."""

from __future__ import annotations

import json
import logging
from typing import Any

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HFValidationError, HfHubHTTPError

logger = logging.getLogger(__name__)


def _message_content_to_string(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if not part or not isinstance(part, dict) or "text" not in part:
                parts.append("")
                continue
            text = part.get("text")
            parts.append(text if isinstance(text, str) else "")
        return "".join(parts)
    return ""


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


def _normalize_text_generation_output(out: Any) -> str:
    if isinstance(out, str):
        return out.strip()
    if isinstance(out, dict) and "generated_text" in out:
        return str(out["generated_text"]).strip()
    if hasattr(out, "generated_text"):
        return str(getattr(out, "generated_text")).strip()
    return ""


def generate_answer(
    model: str,
    access_token: str,
    prompt: str,
    provider_policy: str = "hf-inference",
) -> str:
    """
    Chat completions, then text generation. Retries each with `auto` routing if the
    configured provider has no mapping for the model.
    """
    providers = _providers_to_try(provider_policy)

    for provider in providers:
        try:
            client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
            out = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
            )
            choice0 = out.choices[0] if out.choices else None
            raw = choice0.message.content if choice0 and choice0.message else None
            text = _message_content_to_string(raw).strip()
            if text:
                return text
        except Exception as err:
            if isinstance(err, (HfHubHTTPError, HFValidationError)):
                _log_hf_error("chatCompletion", str(provider), err)

    for provider in providers:
        try:
            client = InferenceClient(model=model, token=access_token, provider=provider)  # type: ignore[arg-type]
            out = client.text_generation(
                prompt,
                max_new_tokens=512,
                return_full_text=False,
            )
            generated = _normalize_text_generation_output(out)
            if generated:
                return generated
        except Exception as err:
            if isinstance(err, (HfHubHTTPError, HFValidationError)):
                _log_hf_error("textGeneration", str(provider), err)

    raise RuntimeError(
        f'No inference provider could run model "{model}". Try HUGGINGFACE_PROVIDER=auto, '
        "pick another HUGGINGFACE_MODEL, or enable a provider at "
        "https://huggingface.co/settings/inference-providers",
    )

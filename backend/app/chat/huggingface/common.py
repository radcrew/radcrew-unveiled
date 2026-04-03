from __future__ import annotations

import json
import logging
from typing import Any

from huggingface_hub.errors import HFValidationError, HfHubHTTPError

logger = logging.getLogger(__name__)

DETERMINISTIC_GENERATION_SEED = 42


def safe_get(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def providers_to_try(provider_policy: str) -> list[str]:
    if provider_policy == "auto":
        return ["auto"]
    return [provider_policy, "auto"]


def log_hf_error(phase: str, provider: str, err: BaseException) -> None:
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

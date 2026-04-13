import logging
from typing import Any

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


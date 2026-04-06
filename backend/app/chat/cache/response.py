"""LRU cache for full RAG prompt → assistant text (tool/feedback path does not use this)."""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from collections.abc import Iterator
from threading import Lock

RESPONSE_CACHE_MAX_SIZE = 256

_response_cache: OrderedDict[str, str] = OrderedDict()
_response_cache_lock = Lock()


def prompt_cache_key(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def get_cached_response(key: str) -> str | None:
    with _response_cache_lock:
        value = _response_cache.get(key)

        if value is None:
            return None

        _response_cache.move_to_end(key)
        return value


def set_cached_response(key: str, value: str) -> None:
    if not value:
        return

    with _response_cache_lock:
        _response_cache[key] = value
        _response_cache.move_to_end(key)

        while len(_response_cache) > RESPONSE_CACHE_MAX_SIZE:
            _response_cache.popitem(last=False)


def stream_answer_with_cache(
    answer_stream: Iterator[str],
    cache_key: str,
) -> Iterator[str]:
    parts: list[str] = []

    for chunk in answer_stream:
        if chunk:
            parts.append(chunk)
            yield chunk

    set_cached_response(cache_key, "".join(parts))


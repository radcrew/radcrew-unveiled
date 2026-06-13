"""LRU response cache: keying, get/set, eviction, and streaming wrapper."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from app.chatbot.graph.nodes.rag_answer import cache as cache_mod
from app.chatbot.graph.nodes.rag_answer.cache import (
    RESPONSE_CACHE_MAX_SIZE,
    get_cached_response,
    prompt_cache_key,
    set_cached_response,
    stream_answer_with_cache,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> Iterator[None]:
    """Cache is a module-level global; isolate every test."""
    cache_mod._response_cache.clear()
    yield
    cache_mod._response_cache.clear()


def test_prompt_cache_key_is_stable_and_distinct() -> None:
    assert prompt_cache_key("hello") == prompt_cache_key("hello")
    assert prompt_cache_key("hello") != prompt_cache_key("world")


def test_get_set_round_trip() -> None:
    key = prompt_cache_key("prompt")
    assert get_cached_response(key) is None
    set_cached_response(key, "answer")
    assert get_cached_response(key) == "answer"


def test_empty_value_is_not_cached() -> None:
    key = prompt_cache_key("prompt")
    set_cached_response(key, "")
    assert get_cached_response(key) is None


def test_eviction_drops_oldest_when_over_capacity() -> None:
    for i in range(RESPONSE_CACHE_MAX_SIZE + 1):
        set_cached_response(prompt_cache_key(f"p{i}"), f"v{i}")

    # First inserted key should have been evicted.
    assert get_cached_response(prompt_cache_key("p0")) is None
    # Most recent should remain.
    assert get_cached_response(prompt_cache_key(f"p{RESPONSE_CACHE_MAX_SIZE}")) == (
        f"v{RESPONSE_CACHE_MAX_SIZE}"
    )


def test_get_promotes_entry_to_most_recently_used() -> None:
    # Fill exactly to capacity.
    for i in range(RESPONSE_CACHE_MAX_SIZE):
        set_cached_response(prompt_cache_key(f"p{i}"), f"v{i}")

    # Touch the oldest so it becomes most-recent, then insert one more.
    assert get_cached_response(prompt_cache_key("p0")) == "v0"
    set_cached_response(prompt_cache_key("new"), "vnew")

    # p0 survived; p1 (now oldest) was evicted instead.
    assert get_cached_response(prompt_cache_key("p0")) == "v0"
    assert get_cached_response(prompt_cache_key("p1")) is None


def test_stream_answer_with_cache_yields_and_caches() -> None:
    key = prompt_cache_key("streamed")
    chunks = stream_answer_with_cache(iter(["foo", "", "bar"]), key)

    # Empty chunks are filtered from the yielded stream.
    assert list(chunks) == ["foo", "bar"]
    # Joined non-empty chunks are cached.
    assert get_cached_response(key) == "foobar"

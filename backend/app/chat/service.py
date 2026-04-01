"""Chat orchestration for /chat route."""

from __future__ import annotations

import hashlib
import time
from collections import OrderedDict
from collections.abc import Iterator
from threading import Lock

from app.chat.huggingface import generate_answer
from app.chat.messages import MSG_FALLBACK_LOW_CONTEXT, MSG_MISSING_HF_KEY
from app.chat.prompt import build_chat_prompt
from app.chat.retrieval import retrieve_relevant_chunks, retrieval_fallback_needed
from app.config import get_settings
from app.models import KnowledgeChunk
from app.schemas import ChatRequest

STREAM_TEXT_CHUNK_SIZE = 2
RESPONSE_CACHE_MAX_SIZE = 256

_response_cache: OrderedDict[str, str] = OrderedDict()
_response_cache_lock = Lock()


def _prompt_cache_key(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _cache_get(key: str) -> str | None:
    with _response_cache_lock:
        value = _response_cache.get(key)
        if value is None:
            return None
        # Maintain LRU recency.
        _response_cache.move_to_end(key)
        return value


def _cache_put(key: str, value: str) -> None:
    if not value:
        return
    with _response_cache_lock:
        _response_cache[key] = value
        _response_cache.move_to_end(key)
        while len(_response_cache) > RESPONSE_CACHE_MAX_SIZE:
            _response_cache.popitem(last=False)


def _stream_and_cache(
    answer_stream: Iterator[str],
    cache_key: str,
) -> Iterator[str]:
    parts: list[str] = []
    for chunk in answer_stream:
        if chunk:
            parts.append(chunk)
            yield chunk
    _cache_put(cache_key, "".join(parts))


def stream_text_chunks(text: str, chunk_size: int = STREAM_TEXT_CHUNK_SIZE) -> Iterator[str]:
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


def generate_chat_stream(
    body: ChatRequest,
    knowledge_chunks: list[KnowledgeChunk],
) -> Iterator[str]:
    settings = get_settings()

    message = body.message
    history = body.history or []
    recent_user_turns = [m.content for m in history if m.role == "user" and m.content]

    retrieval_query = message
    if recent_user_turns:
        recent_context = "\n".join(recent_user_turns[-2:])
        retrieval_query = f"{message}\n\nPrevious user context:\n{recent_context}"

    relevant_chunks = retrieve_relevant_chunks(
        knowledge_chunks,
        retrieval_query,
        5,
        embedding_access_token=settings.HUGGINGFACE_API_KEY,
        embedding_model=settings.HUGGINGFACE_EMBEDDING_MODEL,
        embedding_provider=settings.HUGGINGFACE_EMBEDDING_PROVIDER,
    )

    if retrieval_fallback_needed(relevant_chunks) and not history:
        return stream_text_chunks(MSG_FALLBACK_LOW_CONTEXT)

    if not settings.HUGGINGFACE_API_KEY:
        return stream_text_chunks(MSG_MISSING_HF_KEY)

    prompt = build_chat_prompt(message, relevant_chunks, history=history)
    cache_key = _prompt_cache_key(prompt)
    cached = _cache_get(cache_key)
    if cached is not None:
        return stream_text_chunks(cached)

    return _stream_and_cache(
        generate_answer(
            settings.HUGGINGFACE_MODEL,
            settings.HUGGINGFACE_API_KEY,
            prompt,
            settings.HUGGINGFACE_PROVIDER,
        ),
        cache_key,
    )

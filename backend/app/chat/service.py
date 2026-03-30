"""Chat orchestration for /chat route."""

from __future__ import annotations

import hashlib
import time
from collections.abc import Iterator
from collections import OrderedDict
from threading import Lock

from app.chat.huggingface import generate_answer
from app.chat.messages import MSG_FALLBACK_LOW_CONTEXT, MSG_MISSING_HF_KEY
from app.chat.prompt import build_chat_prompt
from app.chat.retrieval import retrieve_relevant_chunks, retrieval_fallback_needed
from app.config import get_settings
from app.models import KnowledgeChunk, KnowledgeChunkScored
from app.schemas import ChatRequest

STREAM_TEXT_CHUNK_SIZE = 24
FALLBACK_STREAM_CHUNK_DELAY_SECONDS = 0.03
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


def scored_to_chunk(scored: KnowledgeChunkScored) -> KnowledgeChunk:
    return KnowledgeChunk(
        id=scored.id,
        title=scored.title,
        text=scored.text,
        tokens=scored.tokens,
        url=scored.url,
    )


def stream_text_chunks(text: str, chunk_size: int = STREAM_TEXT_CHUNK_SIZE) -> Iterator[str]:
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size]
        if chunk:
            yield chunk
            # Make synthetic fallback messages feel like real streaming in the UI.
            time.sleep(FALLBACK_STREAM_CHUNK_DELAY_SECONDS)


def stream_chat_request(
    body: ChatRequest,
    knowledge_chunks: list[KnowledgeChunk],
) -> tuple[Iterator[str], float]:
    settings = get_settings()
    message = body.message

    # Memory: `history` should be included both in retrieval and in the prompt.
    # We keep retrieval query bounded by only using the most recent user turns.
    history = body.history or []
    recent_user_turns = [m.content for m in history if m.role == "user" and m.content]
    retrieval_query = message
    if recent_user_turns:
        recent_context = "\n".join(recent_user_turns[-2:])
        retrieval_query = f"{message}\n\nPrevious user context:\n{recent_context}"

    relevant = retrieve_relevant_chunks(
        knowledge_chunks,
        retrieval_query,
        5,
        embedding_access_token=settings.HUGGINGFACE_API_KEY,
        embedding_model=settings.HUGGINGFACE_EMBEDDING_MODEL,
        embedding_provider=settings.HUGGINGFACE_EMBEDDING_PROVIDER,
    )

    # If there is conversation history, allow the model to answer from that memory
    # even when RAG retrieval is weak for the current standalone wording.
    if retrieval_fallback_needed(relevant) and not history:
        return stream_text_chunks(MSG_FALLBACK_LOW_CONTEXT), 0.2

    if not settings.HUGGINGFACE_API_KEY:
        return stream_text_chunks(MSG_MISSING_HF_KEY), 0

    context_chunks = [scored_to_chunk(c) for c in relevant]
    prompt = build_chat_prompt(message, context_chunks, history=history)
    cache_key = _prompt_cache_key(prompt)
    cached = _cache_get(cache_key)
    if cached is not None:
        return stream_text_chunks(cached), min(1.0, relevant[0].score / 3)

    confidence = min(1.0, relevant[0].score / 3) if relevant else 0.6
    return (
        _stream_and_cache(
            generate_answer(
                settings.HUGGINGFACE_MODEL,
                settings.HUGGINGFACE_API_KEY,
                prompt,
                settings.HUGGINGFACE_PROVIDER,
            ),
            cache_key,
        ),
        confidence,
    )

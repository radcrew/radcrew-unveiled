"""Retrieval, prompt build, response cache, and streaming answer for the FAQ RAG path."""

from __future__ import annotations

from collections.abc import Iterator

from app.config import get_settings

from app.chat.cache.response import (
    get_cached_response,
    get_text_chunk_stream,
    prompt_cache_key,
    stream_answer_with_cache,
)
from app.chat.huggingface import generate_answer
from app.chat.messages import MSG_FALLBACK_LOW_CONTEXT, MSG_MISSING_HF_KEY
from app.chat.rag.prompt import build_chat_prompt
from app.chat.rag.retrieval import retrieve_relevant_chunks, retrieval_fallback_needed
from app.config import get_settings
from app.knowledge.models import KnowledgeChunk
from app.schemas import ChatRequest


def stream_rag_chat_answer(
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
        5
    )

    if retrieval_fallback_needed(relevant_chunks) and not history:
        return get_text_chunk_stream(MSG_FALLBACK_LOW_CONTEXT)

    if not settings.HUGGINGFACE_API_KEY:
        return get_text_chunk_stream(MSG_MISSING_HF_KEY)

    prompt = build_chat_prompt(message, relevant_chunks, history=history)

    cache_key = prompt_cache_key(prompt)
    cached = get_cached_response(cache_key)
    if cached is not None:
        return get_text_chunk_stream(cached)

    return stream_answer_with_cache(
        generate_answer(
            settings.HUGGINGFACE_MODEL,
            settings.HUGGINGFACE_API_KEY,
            prompt,
            settings.HUGGINGFACE_PROVIDER,
        ),
        cache_key,
    )

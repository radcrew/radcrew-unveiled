"""Chat orchestration for /chat route."""

from __future__ import annotations

import time
from collections.abc import Iterator

from app.chat.huggingface import generate_answer
from app.chat.messages import MSG_FALLBACK_LOW_CONTEXT, MSG_MISSING_HF_KEY
from app.chat.prompt import build_chat_prompt
from app.chat.retrieval import retrieve_relevant_chunks, retrieval_fallback_needed
from app.config import get_settings
from app.models import KnowledgeChunk, KnowledgeChunkScored
from app.schemas import ChatRequest

STREAM_TEXT_CHUNK_SIZE = 24
FALLBACK_STREAM_CHUNK_DELAY_SECONDS = 0.03


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
    message = body.message
    relevant = retrieve_relevant_chunks(knowledge_chunks, message, 5)

    if retrieval_fallback_needed(relevant):
        return stream_text_chunks(MSG_FALLBACK_LOW_CONTEXT), 0.2

    settings = get_settings()
    if not settings.HUGGINGFACE_API_KEY:
        return stream_text_chunks(MSG_MISSING_HF_KEY), 0

    context_chunks = [scored_to_chunk(c) for c in relevant]
    prompt = build_chat_prompt(message, context_chunks)
    return (
        generate_answer(
            settings.HUGGINGFACE_MODEL,
            settings.HUGGINGFACE_API_KEY,
            prompt,
            settings.HUGGINGFACE_PROVIDER,
        ),
        min(1.0, relevant[0].score / 3),
    )

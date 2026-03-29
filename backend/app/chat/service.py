"""Chat orchestration for /chat route."""

from __future__ import annotations

from app.chat.huggingface import generate_answer
from app.chat.messages import MSG_FALLBACK_LOW_CONTEXT, MSG_MISSING_HF_KEY
from app.chat.prompt import build_chat_prompt
from app.chat.retrieval import retrieve_relevant_chunks, retrieval_fallback_needed
from app.config import get_settings
from app.models import KnowledgeChunk, KnowledgeChunkScored
from app.schemas import ChatRequest


def scored_to_chunk(scored: KnowledgeChunkScored) -> KnowledgeChunk:
    return KnowledgeChunk(
        id=scored.id,
        title=scored.title,
        text=scored.text,
        tokens=scored.tokens,
        url=scored.url,
    )


def handle_chat_request(
    body: ChatRequest,
    knowledge_chunks: list[KnowledgeChunk],
) -> dict:
    message = body.message
    relevant = retrieve_relevant_chunks(knowledge_chunks, message, 5)

    if retrieval_fallback_needed(relevant):
        return {
            "answer": MSG_FALLBACK_LOW_CONTEXT,
            "confidence": 0.2,
        }

    settings = get_settings()
    if not settings.HUGGINGFACE_API_KEY:
        return {
            "answer": MSG_MISSING_HF_KEY,
            "confidence": 0,
        }

    context_chunks = [scored_to_chunk(c) for c in relevant]
    prompt = build_chat_prompt(message, context_chunks)
    answer = generate_answer(
        settings.HUGGINGFACE_MODEL,
        settings.HUGGINGFACE_API_KEY,
        prompt,
        settings.HUGGINGFACE_PROVIDER,
    )

    return {
        "answer": answer,
        "confidence": min(1.0, relevant[0].score / 3),
    }

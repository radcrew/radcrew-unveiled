"""RAG path: retrieval, prompts, embedding config, streamed answers."""

from __future__ import annotations

from app.chatbot.rag.models import EmbeddingInferenceConfig
from app.chatbot.rag.prompt import build_chat_prompt
from app.chatbot.rag.retrieval import (
    RETRIEVAL_FALLBACK_SCORE_THRESHOLD,
    build_knowledge_chunks,
    retrieval_fallback_needed,
    retrieve_relevant_chunks,
    tokenize,
)
from app.chatbot.rag.stream import stream_rag_chat_answer

__all__ = [
    "RETRIEVAL_FALLBACK_SCORE_THRESHOLD",
    "EmbeddingInferenceConfig",
    "build_chat_prompt",
    "build_knowledge_chunks",
    "retrieval_fallback_needed",
    "retrieve_relevant_chunks",
    "stream_rag_chat_answer",
    "tokenize",
]

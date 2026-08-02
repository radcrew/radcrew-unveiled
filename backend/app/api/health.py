"""Health check endpoint."""

from fastapi import APIRouter

from app.chatbot import chat
from app.chatbot.knowledge.indexing import last_index_ok
from app.core.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str | int | bool]:
    """Report readiness plus the two config facts that explain most outages.

    A deployed instance that answers requests but cannot generate looks
    identical from outside: chat fails somewhere inside a stream that has
    already returned 200. ``provider`` says which backend is selected (or
    "none", meaning no credential is set), and ``embeddings`` says whether
    semantic retrieval is available or has silently dropped to lexical
    matching.

    ``vector_store`` is false when no database is configured, and also when one
    is configured but startup indexing did not complete, which is the same class
    of silent degradation: retrieval keeps answering, quietly, from whatever the
    store already held. It reports the last indexing outcome rather than probing
    the database, so this public endpoint issues no queries of its own.

    This endpoint is public, so it reports names and booleans only, never
    credentials, model ids, or allowed origins.
    """
    settings = get_settings()
    # "chunks" is the documented response field; the value is the document count.
    return {
        "ok": True,
        "chunks": len(chat.knowledge_documents),
        "provider": settings.llm_provider(),
        "embeddings": bool(settings.HF_TOKEN),
        "vector_store": settings.vector_store_enabled() and last_index_ok(),
    }

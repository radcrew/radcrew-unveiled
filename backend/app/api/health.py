"""Health check endpoint."""

from fastapi import APIRouter

from app.chatbot import chat
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
    }

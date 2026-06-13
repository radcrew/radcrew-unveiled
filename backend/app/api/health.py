"""Health check endpoint."""

from fastapi import APIRouter

from app.chatbot import chat

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, int | bool]:
    # "chunks" is the documented response field; the value is the document count.
    return {"ok": True, "chunks": len(chat.knowledge_documents)}

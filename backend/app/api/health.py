"""Health check endpoint."""

from fastapi import APIRouter

from app.chatbot import chat

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, int | bool]:
    return {"ok": True, "chunks": len(chat.knowledge_chunks)}

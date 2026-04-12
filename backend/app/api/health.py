"""Health check endpoint."""

from fastapi import APIRouter

from app.chatbot import chatbot_logic

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, int | bool]:
    return {"ok": True, "chunks": len(chatbot_logic.knowledge_chunks)}

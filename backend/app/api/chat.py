"""SSE chat endpoint."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.chatbot import chatbot_logic
from app.chatbot.messages import MSG_AI_UNAVAILABLE
from app.schemas import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(body: ChatRequest) -> StreamingResponse:
    try:
        answer_stream = chatbot_logic.generate_chat_stream(body, chatbot_logic.knowledge_chunks)
    except Exception:
        logger.exception("POST /chat failed")
        answer_stream = iter([MSG_AI_UNAVAILABLE])

    def event_stream():
        for chunk in answer_stream:
            if chunk:
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

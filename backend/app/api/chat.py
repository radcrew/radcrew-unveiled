"""SSE chat endpoint."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.chatbot import chat as chatbot
from app.chatbot.messages import MSG_AI_UNAVAILABLE
from app.schemas import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(body: ChatRequest) -> StreamingResponse:
    try:
        answer_stream = chatbot.generate_chat_stream(body)
    except Exception:
        logger.exception("POST /chat failed")
        answer_stream = iter([MSG_AI_UNAVAILABLE])

    def event_stream():
        # The answer is a chain of lazy generators (retrieval, guardrails, HF
        # streaming), so nothing above has run yet. An error raised here escapes
        # into the ASGI server *after* the 200 headers are already on the wire,
        # which the client sees as an empty body and no error at all. Catch it,
        # log the real traceback, and close the stream with the fallback message.
        try:
            for chunk in answer_stream:
                if chunk:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception:
            logger.exception("POST /chat stream failed")
            yield f"data: {json.dumps({'type': 'chunk', 'content': MSG_AI_UNAVAILABLE})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

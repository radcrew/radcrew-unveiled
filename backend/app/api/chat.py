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
        answer = chatbot.generate_chat_stream(body)
    except Exception:
        logger.exception("POST /chat failed")
        answer = chatbot.ChatStream(iter([MSG_AI_UNAVAILABLE]))

    def event_stream():
        # The answer is a chain of lazy generators (retrieval, guardrails, HF
        # streaming), so nothing above has run yet. An error raised here escapes
        # into the ASGI server *after* the 200 headers are already on the wire,
        # which the client sees as an empty body and no error at all. Catch it,
        # log the real traceback, and close the stream with the fallback message.
        try:
            for chunk in answer.chunks:
                if chunk:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception:
            logger.exception("POST /chat stream failed")
            yield f"data: {json.dumps({'type': 'chunk', 'content': MSG_AI_UNAVAILABLE})}\n\n"
        else:
            # Only after a complete answer. The failure branch above already said
            # the answer is unavailable, and follow-up chips under an apology
            # offer questions we just failed to answer.
            if answer.hints:
                yield f"data: {json.dumps({'type': 'hints', 'hints': list(answer.hints)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

import logging
import json

from fastapi.responses import StreamingResponse

from app.chat.messages import MSG_AI_UNAVAILABLE
from app.chat.service import generate_chat_stream
from app.bootstrap import create_lifespan
from app.config import get_settings
from app.http import create_http_app
from app.knowledge.models import KnowledgeChunk
from app.schemas import ChatRequest

logger = logging.getLogger(__name__)

_settings = get_settings()
PORT = _settings.PORT
FRONTEND_ORIGIN = _settings.FRONTEND_ORIGIN

knowledge_chunks: list[KnowledgeChunk] = []

def _set_knowledge_chunks(chunks: list[KnowledgeChunk]) -> None:
    global knowledge_chunks
    knowledge_chunks = chunks


app = create_http_app(
    frontend_origin=FRONTEND_ORIGIN,
    lifespan=create_lifespan(_set_knowledge_chunks),
)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "chunks": len(knowledge_chunks)}


@app.post("/chat")
def chat(body: ChatRequest) -> StreamingResponse:
    try:
        answer_stream = generate_chat_stream(body, knowledge_chunks)
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT)

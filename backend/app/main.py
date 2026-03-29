import logging

from fastapi.responses import JSONResponse

from app.chat.messages import MSG_AI_UNAVAILABLE
from app.chat.service import handle_chat_request
from app.bootstrap import create_lifespan
from app.config import get_settings
from app.http import create_http_app
from app.models import KnowledgeChunk
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


@app.post("/chat", response_model=None)
def chat(body: ChatRequest) -> dict | JSONResponse:
    try:
        return handle_chat_request(body, knowledge_chunks)
    except Exception:
        logger.exception("POST /chat failed")
        return JSONResponse(
            status_code=502,
            content={"error": MSG_AI_UNAVAILABLE},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT)

import logging
from collections.abc import Iterator

from app.chatbot.deepsearch import deep_search_documents, is_deep_search_available
from app.chatbot.messages import MSG_FALLBACK_LOW_CONTEXT
from app.chatbot.graph.state import ChatState
from app.chatbot.utils import get_text_chunk_stream
from app.chatbot.huggingface import generate_answer
from app.core.settings import get_settings
from .prompt import build_chat_prompt
from .retrieval import retrieve_with_confidence
from .sanitize import sanitize_answer_stream
from .cache import (
    get_cached_response,
    prompt_cache_key,
    stream_answer_with_cache,
)

logger = logging.getLogger(__name__)


def rag_answer_node(state: ChatState) -> dict[str, Iterator[str]]:
    settings = get_settings()
    body = state["body"]
    knowledge_chunks = state["knowledge_chunks"]

    message = body.message
    history = body.history or []
    user_messages = [m.content for m in history if m.role == "user" and m.content]

    recent_context = "\n".join(user_messages[-2:])
    retrieval_query = f"{message}\n\nPrevious user context:\n{recent_context}"

    relevant_chunks, confidence = retrieve_with_confidence(
        knowledge_chunks,
        retrieval_query,
        8,
    )

    # Deep search fallback: only when the knowledge base can't confidently answer.
    context_chunks = list(knowledge_chunks)
    web_chunks = []
    if confidence < settings.DEEP_SEARCH_SIMILARITY_THRESHOLD and is_deep_search_available():
        web_chunks = deep_search_documents(message)
        logger.info(
            "[deepsearch] triggered confidence=%.3f results=%d message=%r",
            confidence,
            len(web_chunks),
            message[:120],
        )
        context_chunks += web_chunks

    if not relevant_chunks and not web_chunks and not history:
        return {"output_stream": get_text_chunk_stream(MSG_FALLBACK_LOW_CONTEXT)}

    prompt = build_chat_prompt(message, context_chunks, history)

    cache_key = prompt_cache_key(prompt.cache_text())
    cached = get_cached_response(cache_key)
    if cached is not None:
        return {"output_stream": get_text_chunk_stream(cached)}

    return {
        "output_stream": stream_answer_with_cache(
            sanitize_answer_stream(
                generate_answer(prompt.system, prompt.user, list(prompt.history))
            ),
            cache_key,
        )
    }
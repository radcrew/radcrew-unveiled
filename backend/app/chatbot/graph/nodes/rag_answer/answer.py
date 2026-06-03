import logging
from collections.abc import Iterator
from time import perf_counter

from app.chatbot.deepsearch import deep_search_documents, is_deep_search_available
from app.chatbot.messages import MSG_FALLBACK_LOW_CONTEXT
from app.chatbot.graph.state import ChatState
from app.chatbot.graph.nodes.feedback_router.pregate import looks_like_question
from app.chatbot.utils import get_text_chunk_stream, timed_stream
from app.chatbot.huggingface import generate_answer
from app.core.settings import get_settings
from .prompt import build_chat_prompt
from .retrieval import query_matches_known_title, retrieve_with_confidence
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

    retrieval_start = perf_counter()
    relevant_chunks, confidence = retrieve_with_confidence(
        knowledge_chunks,
        retrieval_query,
        8,
    )
    logger.info(
        "[timing] retrieval=%.3fs confidence=%.3f chunks=%d",
        perf_counter() - retrieval_start,
        confidence,
        len(relevant_chunks),
    )

    # Deep search fallback: only when the knowledge base can't confidently answer
    # AND the message is an actual information request. Chit-chat, corrections, or
    # identity claims ("you were created by X") must not pull in web results —
    # that injects irrelevant junk the model then parrots.
    context_chunks = list(knowledge_chunks)
    web_chunks = []
    # A low semantic score alone is not "out of scope": short name lookups like
    # "who is Jesus?" always score low yet match a profile title. If a query token
    # hits a known title, the KB covers it — skip the web fallback so it can't
    # override the right answer with same-named web noise (e.g. Jesus Christ).
    deep_search_eligible = (
        confidence < settings.DEEP_SEARCH_SIMILARITY_THRESHOLD
        and looks_like_question(message)
        and not query_matches_known_title(knowledge_chunks, message)
        and is_deep_search_available()
    )
    if deep_search_eligible:
        deep_search_start = perf_counter()
        web_chunks = deep_search_documents(message)
        logger.info(
            "[deepsearch] triggered confidence=%.3f results=%d elapsed=%.3fs message=%r",
            confidence,
            len(web_chunks),
            perf_counter() - deep_search_start,
            message[:120],
        )
        context_chunks += web_chunks

    if not relevant_chunks and not web_chunks and not history:
        return {"output_stream": get_text_chunk_stream(MSG_FALLBACK_LOW_CONTEXT)}

    prompt = build_chat_prompt(message, context_chunks, history)

    cache_key = prompt_cache_key(prompt.cache_text())
    cached = get_cached_response(cache_key)
    if cached is not None:
        logger.info("[timing] cache=hit chars=%d", len(cached))
        return {"output_stream": get_text_chunk_stream(cached)}

    return {
        "output_stream": timed_stream(
            stream_answer_with_cache(
                sanitize_answer_stream(
                    generate_answer(prompt.system, prompt.user, list(prompt.history))
                ),
                cache_key,
            ),
            "generation",
        )
    }
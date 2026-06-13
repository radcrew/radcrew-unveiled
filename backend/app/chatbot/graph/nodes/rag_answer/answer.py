"""LangGraph node: retrieve context, optionally web-search, and stream the answer."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from time import perf_counter

from app.chatbot.deepsearch import deep_search_documents, is_deep_search_available
from app.chatbot.graph.nodes.feedback_router.pregate import (
    is_smalltalk,
    looks_like_question,
)
from app.chatbot.graph.state import ChatState
from app.chatbot.guardrails import apply_output_rail_stream
from app.chatbot.huggingface import generate_answer
from app.chatbot.knowledge.models import KnowledgeDocument
from app.chatbot.messages import MSG_FALLBACK_LOW_CONTEXT
from app.chatbot.utils import get_text_chunk_stream, timed_stream
from app.core.settings import Settings, get_settings

from .cache import get_cached_response, prompt_cache_key, stream_answer_with_cache
from .prompt import ChatPrompt, build_chat_prompt, build_smalltalk_prompt
from .retrieval import query_matches_known_title, retrieve_with_confidence
from .sanitize import sanitize_answer_stream

logger = logging.getLogger(__name__)

# How many knowledge documents to retrieve as context for an answer.
RETRIEVAL_DOCUMENT_LIMIT = 8


def rag_answer_node(state: ChatState) -> dict[str, Iterator[str]]:
    settings = get_settings()
    body = state["body"]
    knowledge_documents = state["knowledge_documents"]

    message = body.message
    history = body.history or []

    # Pure greetings / chit-chat are not grounded in the knowledge base. Answer
    # them conversationally with the small-talk persona, skipping retrieval, the
    # low-context fallback, and the groundedness rail (which would always flag a
    # greeting as ungrounded).
    if is_smalltalk(message):
        prompt = build_smalltalk_prompt(message, history)
        return _stream_prompt(prompt, context_documents=[], skip_groundedness=True)

    user_messages = [m.content for m in history if m.role == "user" and m.content]
    recent_context = "\n".join(user_messages[-2:])
    retrieval_query = f"{message}\n\nPrevious user context:\n{recent_context}"

    retrieval_start = perf_counter()
    retrieved_documents, confidence = retrieve_with_confidence(
        knowledge_documents,
        retrieval_query,
        RETRIEVAL_DOCUMENT_LIMIT,
    )
    logger.info(
        "[timing] retrieval=%.3fs confidence=%.3f documents=%d",
        perf_counter() - retrieval_start,
        confidence,
        len(retrieved_documents),
    )

    context_documents = list(knowledge_documents)
    web_documents = _maybe_deep_search(message, confidence, knowledge_documents, settings)
    context_documents += web_documents

    if not retrieved_documents and not web_documents and not history:
        return {"output_stream": get_text_chunk_stream(MSG_FALLBACK_LOW_CONTEXT)}

    prompt = build_chat_prompt(message, context_documents, history)
    return _stream_prompt(prompt, context_documents, skip_groundedness=False)


def _maybe_deep_search(
    message: str,
    confidence: float,
    knowledge_documents: list[KnowledgeDocument],
    settings: Settings,
) -> list[KnowledgeDocument]:
    """Web-search fallback, used only when the knowledge base can't confidently answer.

    Restricted to genuine information requests. Chit-chat, corrections, or
    identity claims ("you were created by X") must not pull in web results —
    that injects irrelevant junk the model then parrots. A low semantic score
    alone is not "out of scope" either: short name lookups like "who is Jesus?"
    score low yet match a profile title, so a known-title hit suppresses the
    fallback to avoid same-named web noise (e.g. Jesus Christ).
    """
    eligible = (
        confidence < settings.DEEP_SEARCH_SIMILARITY_THRESHOLD
        and looks_like_question(message)
        and not query_matches_known_title(knowledge_documents, message)
        and is_deep_search_available()
    )
    if not eligible:
        return []

    start = perf_counter()
    web_documents = deep_search_documents(message)
    logger.info(
        "[deepsearch] triggered confidence=%.3f results=%d elapsed=%.3fs message=%r",
        confidence,
        len(web_documents),
        perf_counter() - start,
        message[:120],
    )
    return web_documents


def _stream_prompt(
    prompt: ChatPrompt,
    context_documents: list[KnowledgeDocument],
    skip_groundedness: bool,
) -> dict[str, Iterator[str]]:
    """Serve a built prompt: cache hit → replay, else stream through the rails."""
    cache_key = prompt_cache_key(prompt.cache_text())
    cached = get_cached_response(cache_key)
    if cached is not None:
        logger.info("[timing] cache=hit chars=%d", len(cached))
        return {"output_stream": get_text_chunk_stream(cached)}

    return {
        "output_stream": timed_stream(
            stream_answer_with_cache(
                apply_output_rail_stream(
                    sanitize_answer_stream(
                        generate_answer(prompt.system, prompt.user, list(prompt.history))
                    ),
                    context_documents,
                    skip_groundedness=skip_groundedness,
                ),
                cache_key,
            ),
            "generation",
        )
    }

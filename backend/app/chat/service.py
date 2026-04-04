"""Chat orchestration for /chat route."""

from __future__ import annotations

import hashlib
import json
import logging
from collections import OrderedDict
from collections.abc import Iterator
from threading import Lock
from typing import Any

from app.chat.huggingface import generate_answer
from app.chat.huggingface.tool_routing import route_tool_calls
from app.chat.messages import (
    MSG_FALLBACK_LOW_CONTEXT,
    MSG_FEEDBACK_NOT_CONFIGURED,
    MSG_FEEDBACK_SEND_FAILED,
    MSG_FEEDBACK_THANKS,
    MSG_MISSING_HF_KEY,
)
from app.chat.prompt import build_chat_prompt
from app.chat.models import EmbeddingInferenceConfig
from app.chat.retrieval import retrieve_relevant_chunks, retrieval_fallback_needed
from app.config import get_settings
from app.feedback.web3forms import (
    FeedbackNotConfiguredError,
    FeedbackSubmissionError,
    FeedbackValidationError,
    submit_feedback_via_web3forms,
)
from app.knowledge.models import KnowledgeChunk
from app.schemas import ChatHistoryMessage, ChatRequest

logger = logging.getLogger(__name__)

STREAM_TEXT_CHUNK_SIZE = 2
RESPONSE_CACHE_MAX_SIZE = 256

_response_cache: OrderedDict[str, str] = OrderedDict()
_response_cache_lock = Lock()


def _get_prompt_cache_key(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _get_response_cache(key: str) -> str | None:
    with _response_cache_lock:
        value = _response_cache.get(key)
        if value is None:
            return None
        # Maintain LRU recency.
        _response_cache.move_to_end(key)
        return value


def _set_response_cache(key: str, value: str) -> None:
    if not value:
        return
    with _response_cache_lock:
        _response_cache[key] = value
        _response_cache.move_to_end(key)
        while len(_response_cache) > RESPONSE_CACHE_MAX_SIZE:
            _response_cache.popitem(last=False)


def _stream_and_cache_response(
    answer_stream: Iterator[str],
    cache_key: str,
) -> Iterator[str]:
    parts: list[str] = []
    for chunk in answer_stream:
        if chunk:
            parts.append(chunk)
            yield chunk
    _set_response_cache(cache_key, "".join(parts))


def get_text_chunk_stream(
    text: str, chunk_size: int = STREAM_TEXT_CHUNK_SIZE
) -> Iterator[str]:
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


def _tool_routing_messages(
    message: str, history: list[ChatHistoryMessage]
) -> list[dict[str, Any]]:
    """Up to two prior user turns from history, then the latest user message."""
    recent_user_turns = [m.content for m in history if m.role == "user" and m.content]
    prior = recent_user_turns[-2:]
    msgs: list[dict[str, Any]] = [{"role": "user", "content": c} for c in prior]
    msgs.append({"role": "user", "content": message})
    return msgs


def generate_chat_stream(
    body: ChatRequest,
    knowledge_chunks: list[KnowledgeChunk],
) -> Iterator[str]:
    settings = get_settings()

    message = body.message
    history = body.history or []
    recent_user_turns = [m.content for m in history if m.role == "user" and m.content]

    if settings.HUGGINGFACE_API_KEY:
        try:
            tool_msgs = _tool_routing_messages(message, history)
            routed = route_tool_calls(
                settings.HUGGINGFACE_MODEL,
                settings.HUGGINGFACE_API_KEY,
                tool_msgs,
                settings.HUGGINGFACE_PROVIDER,
            )
        except Exception as exc:
            logger.exception("[chat] tool routing failed: %s", exc)
            routed = []

        advice_call = next((c for c in routed if c.name == "send_company_advice"), None)
        if advice_call is not None:
            args: dict[str, Any] | None = None
            try:
                parsed = json.loads(advice_call.arguments)
                args = parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                logger.warning("[chat] could not parse send_company_advice arguments as JSON")

            if args is not None and isinstance(args.get("message"), str):
                body_text = args["message"]
                raw_subj = args.get("subject")
                subject = raw_subj if isinstance(raw_subj, str) else None
                email = settings.COMPANY_FEEDBACK_EMAIL
                try:
                    submit_feedback_via_web3forms(
                        body_text,
                        subject,
                        settings=settings,
                    )
                except FeedbackNotConfiguredError:
                    logger.warning(
                        "Feedback submission unavailable: WEB3FORMS_ACCESS_KEY is not set."
                    )
                    return get_text_chunk_stream(
                        MSG_FEEDBACK_NOT_CONFIGURED.format(email=email)
                    )
                except (FeedbackValidationError, FeedbackSubmissionError) as exc:
                    logger.warning("Feedback submission failed: %s", exc)
                    return get_text_chunk_stream(MSG_FEEDBACK_SEND_FAILED.format(email=email))

                return get_text_chunk_stream(MSG_FEEDBACK_THANKS.format(email=email))

    retrieval_query = message
    if recent_user_turns:
        recent_context = "\n".join(recent_user_turns[-2:])
        retrieval_query = f"{message}\n\nPrevious user context:\n{recent_context}"

    embedding = EmbeddingInferenceConfig(
        access_token=settings.HUGGINGFACE_API_KEY,
        model=settings.HUGGINGFACE_EMBEDDING_MODEL,
        provider=settings.HUGGINGFACE_EMBEDDING_PROVIDER,
    )
    relevant_chunks = retrieve_relevant_chunks(
        knowledge_chunks,
        retrieval_query,
        5,
        embedding=embedding,
    )

    if retrieval_fallback_needed(relevant_chunks) and not history:
        return get_text_chunk_stream(MSG_FALLBACK_LOW_CONTEXT)

    if not settings.HUGGINGFACE_API_KEY:
        return get_text_chunk_stream(MSG_MISSING_HF_KEY)

    prompt = build_chat_prompt(message, relevant_chunks, history=history)

    cache_key = _get_prompt_cache_key(prompt)
    cached = _get_response_cache(cache_key)
    if cached is not None:
        return get_text_chunk_stream(cached)

    return _stream_and_cache_response(
        generate_answer(
            settings.HUGGINGFACE_MODEL,
            settings.HUGGINGFACE_API_KEY,
            prompt,
            settings.HUGGINGFACE_PROVIDER,
        ),
        cache_key,
    )

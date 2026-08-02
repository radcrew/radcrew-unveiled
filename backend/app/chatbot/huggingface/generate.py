"""Answer generation: stream from the first inference path/provider that responds.

Tries chat-completion across the configured providers first, then falls back to
plain text-generation. Each provider failure is logged and skipped; only when
every path is exhausted is a RuntimeError raised.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from time import sleep

from app.chatbot.huggingface.chat_completion import stream_chat_completion
from app.chatbot.huggingface.common import is_retryable_error, logger, providers_to_try
from app.chatbot.huggingface.text_generation import stream_text_generation
from app.core.settings import get_settings

# A function that streams an answer for one (messages, provider) pair.
StreamFn = Callable[[list[dict[str, str]], str], Iterator[str]]

# Chat-completion attempts per provider before giving up on it. A transient
# router or provider error otherwise costs the whole answer, because the
# text-generation fallback below cannot serve a chat-tuned model: the user gets
# MSG_AI_UNAVAILABLE for a blip a second attempt would have absorbed. Retries
# only ever run on the failure path, so a healthy request pays nothing.
CHAT_COMPLETION_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.25


def generate_answer(
    system: str,
    user: str,
    history: list[dict[str, str]] | None = None,
) -> Iterator[str]:
    settings = get_settings()
    model = settings.HUGGINGFACE_MODEL
    providers = providers_to_try(settings.HUGGINGFACE_PROVIDER)

    # Real multi-turn messages: system, prior turns, then the current question.
    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user})

    produced, chat_error = yield from _stream_first_responding(
        stream_chat_completion,
        messages,
        providers,
        "chatCompletionStream",
        attempts=CHAT_COMPLETION_ATTEMPTS,
    )
    if produced:
        return

    # Text-generation is worth trying for a base model, but not when chat-completion
    # failed for an account reason (402 out of credits, 401/403 bad token): nothing
    # will serve this token, and a chat-tuned model answers that path with "not
    # supported for task text-generation", which then buries the real cause as the
    # last line in the log.
    if chat_error is None or is_retryable_error(chat_error):
        produced, _ = yield from _stream_first_responding(
            stream_text_generation, messages, providers, "textGenerationStream"
        )
        if produced:
            return

    cause = f": {' '.join(str(chat_error).split())}" if chat_error else ""
    raise RuntimeError(
        f'No inference provider could stream model "{model}"{cause}'
    )


def _stream_first_responding(
    stream_fn: StreamFn,
    messages: list[dict[str, str]],
    providers: list[str],
    label: str,
    attempts: int = 1,
) -> Iterator[str]:
    """Stream from the first provider that produces output.

    Yields that provider's content and returns ``(produced, last_error)`` via the
    generator's return value, consumable with ``yield from``. The error is what
    lets the caller tell "nothing served this" from "the account is out", and
    name the real cause when everything fails.

    A failure that happens *after* content has been yielded ends the answer where
    it broke instead of retrying. Those chunks are already on the wire to the
    browser, so a second attempt would append a whole answer to a partial one.
    """
    last_error: Exception | None = None
    for provider in providers:
        for attempt in range(1, attempts + 1):
            produced = False
            try:
                for content in stream_fn(messages, provider):
                    produced = True
                    yield content
            except Exception as err:
                logger.error(
                    "[HF %s provider=%s attempt=%d/%d] %s",
                    label,
                    provider,
                    attempt,
                    attempts,
                    err,
                )
                last_error = err
                if produced:
                    return True, None
                if not is_retryable_error(err):
                    break
                if attempt < attempts:
                    sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            if produced:
                return True, None
            # An empty stream with no error is a real answer of nothing; retrying
            # the same provider would just repeat it.
            break
    return False, last_error

"""Answer generation: stream from the first inference path/provider that responds.

Tries chat-completion across the configured providers first, then falls back to
plain text-generation. Each provider failure is logged and skipped; only when
every path is exhausted is a RuntimeError raised.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

from app.chatbot.huggingface.chat_completion import stream_chat_completion
from app.chatbot.huggingface.common import logger, providers_to_try
from app.chatbot.huggingface.text_generation import stream_text_generation
from app.core.settings import get_settings

# A function that streams an answer for one (messages, provider) pair.
StreamFn = Callable[[list[dict[str, str]], str], Iterator[str]]


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

    if (yield from _stream_first_responding(
        stream_chat_completion, messages, providers, "chatCompletionStream"
    )):
        return
    if (yield from _stream_first_responding(
        stream_text_generation, messages, providers, "textGenerationStream"
    )):
        return

    raise RuntimeError(
        f'No inference provider could stream model "{model}". Try HUGGINGFACE_PROVIDER=auto, '
        "pick another HUGGINGFACE_MODEL"
    )


def _stream_first_responding(
    stream_fn: StreamFn,
    messages: list[dict[str, str]],
    providers: list[str],
    label: str,
) -> Iterator[str]:
    """Stream from the first provider that produces output.

    Yields that provider's content and returns True (via the generator's return
    value, consumable with ``yield from``); returns False if no provider yielded.
    """
    for provider in providers:
        try:
            produced = False
            for content in stream_fn(messages, provider):
                produced = True
                yield content
            if produced:
                return True
        except Exception as err:
            logger.error("[HF %s provider=%s] %s", label, provider, err)
    return False

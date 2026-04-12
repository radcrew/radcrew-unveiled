from __future__ import annotations
from collections.abc import Iterator
from app.core.config import get_settings
from app.chatbot.huggingface.chat_completion import stream_chat_completion
from app.chatbot.huggingface.common import logger, providers_to_try
from app.chatbot.huggingface.text_generation import stream_text_generation


def generate_answer(prompt: str) -> Iterator[str]:
    settings = get_settings()
    model = settings.HUGGINGFACE_MODEL
    provider_policy = settings.HUGGINGFACE_PROVIDER

    providers = providers_to_try(provider_policy)

    for provider in providers:
        try:
            yielded_any = False
            for content in stream_chat_completion(prompt, provider):
                yielded_any = True
                yield content
            if yielded_any:
                return
        except Exception as err:
            logger.error("[HF chatCompletionStream provider=%s] %s", provider, err)

    for provider in providers:
        try:
            yielded_any = False
            for content in stream_text_generation(prompt, provider):
                yielded_any = True
                yield content
            if yielded_any:
                return
        except Exception as err:
            logger.error("[HF textGenerationStream provider=%s] %s", provider, err)

    raise RuntimeError(
        f'No inference provider could stream model "{model}". Try HUGGINGFACE_PROVIDER=auto, '
        "pick another HUGGINGFACE_MODEL"
    )

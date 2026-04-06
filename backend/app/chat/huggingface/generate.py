from __future__ import annotations
from collections.abc import Iterator
from app.config import get_settings
from huggingface_hub.errors import HFValidationError, HfHubHTTPError
from app.chat.huggingface.chat_completion import stream_chat_completion
from app.chat.huggingface.common import log_hf_error, logger, providers_to_try
from app.chat.huggingface.text_generation import stream_text_generation


def generate_answer(prompt: str) -> Iterator[str]:
    settings = get_settings()
    model = settings.HUGGINGFACE_MODEL
    access_token = settings.HUGGINGFACE_API_KEY
    provider_policy = settings.HUGGINGFACE_PROVIDER

    providers = providers_to_try(provider_policy)

    for provider in providers:
        try:
            yielded_any = False
            for content in stream_chat_completion(model, access_token, prompt, provider):
                yielded_any = True
                yield content
            if yielded_any:
                return
        except Exception as err:
            if isinstance(err, (HfHubHTTPError, HFValidationError)):
                log_hf_error("chatCompletionStream", str(provider), err)
            else:
                logger.error("[HF chatCompletionStream provider=%s] %s", provider, err)

    for provider in providers:
        try:
            yielded_any = False
            for content in stream_text_generation(model, access_token, prompt, provider):
                yielded_any = True
                yield content
            if yielded_any:
                return
        except Exception as err:
            if isinstance(err, (HfHubHTTPError, HFValidationError)):
                log_hf_error("textGenerationStream", str(provider), err)
            else:
                logger.error("[HF textGenerationStream provider=%s] %s", provider, err)

    raise RuntimeError(
        f'No inference provider could stream model "{model}". Try HUGGINGFACE_PROVIDER=auto, '
        "pick another HUGGINGFACE_MODEL, or enable a provider at "
        "https://huggingface.co/settings/inference-providers",
    )

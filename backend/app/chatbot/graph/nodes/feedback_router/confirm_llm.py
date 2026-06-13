"""LLM fallback for ambiguous feedback-confirmation replies (Solution D).

The deterministic gate in :mod:`confirm` resolves clear yes/no replies for free.
When it returns ``unknown`` — terse typos ("yse"), short tokens ("go"), or
free-form replies ("yeah alright fine") — we ask the model to label the reply,
constrained to a tiny JSON schema. Any error, missing token, or unsure result
yields ``"unsure"`` so the caller can fall back to normal routing instead of
blocking on the classifier.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Literal

from huggingface_hub import InferenceClient
from huggingface_hub.inference._generated.types.chat_completion import (
    ChatCompletionInputResponseFormatJSONSchema,
    ChatCompletionInputJSONSchema,
)
from pydantic import BaseModel, Field

from app.core.settings import Settings
from app.chatbot.huggingface.common import DETERMINISTIC_DECODING

logger = logging.getLogger(__name__)

ConfirmDecision = Literal["yes", "no", "unsure"]


class ConfirmationReply(BaseModel):
    """Flat label — easiest shape for the small routing model to emit."""

    decision: ConfirmDecision = Field(
        "unsure",
        description=(
            'The assistant just asked the user to confirm sending a message to '
            'the RadCrew team. Label the reply: "yes" to send, "no" to cancel, '
            '"unsure" if it is unrelated or ambiguous.'
        ),
    )


_INSTRUCTIONS = (
    "You decide whether a short reply confirms or declines sending a message to "
    "the RadCrew team. The assistant just asked the user to confirm.\n"
    'Reply with ONLY one JSON object: {"decision": "yes" | "no" | "unsure"}.\n'
    'Use "yes" for any agreement (yes, yeah, go ahead, ok, sure, even typos like '
    '"yse"). Use "no" for any refusal (no, nope, cancel, never mind). Use '
    '"unsure" only when the reply is genuinely unrelated or ambiguous.'
)

# Few-shot examples cover exactly the cases the deterministic gate cannot:
# transposed typos, bare short tokens, and verbose agreement/refusal.
_FEWSHOT: tuple[tuple[str, str], ...] = (
    ("yse", "yes"),
    ("go", "yes"),
    ("yeah alright fine", "yes"),
    ("nah forget it", "no"),
    ("actually what does radcrew do", "unsure"),
)


def _messages(message: str) -> list[dict[str, Any]]:
    msgs: list[dict[str, Any]] = [{"role": "system", "content": _INSTRUCTIONS}]
    for example_message, example_decision in _FEWSHOT:
        msgs.append({"role": "user", "content": example_message})
        msgs.append({"role": "assistant", "content": json.dumps({"decision": example_decision})})
    msgs.append({"role": "user", "content": message})
    return msgs


def classify_confirmation_via_llm(message: str, settings: Settings) -> ConfirmDecision:
    """Best-effort yes/no/unsure for a confirmation reply; never raises."""
    if not settings.HF_TOKEN:
        return "unsure"
    try:
        client = InferenceClient(
            model=settings.HUGGINGFACE_MODEL,
            token=settings.HF_TOKEN,
            provider=settings.HUGGINGFACE_PROVIDER,
        )  # type: ignore[arg-type]
        resp = client.chat_completion(
            messages=_messages(message),
            max_tokens=64,  # tiny: the classifier only emits a one-word JSON label
            **DETERMINISTIC_DECODING,
            response_format=ChatCompletionInputResponseFormatJSONSchema(
                type="json_schema",
                json_schema=ChatCompletionInputJSONSchema(
                    name="confirmation_reply",
                    description="Confirm or decline sending the message to the team.",
                    schema=ConfirmationReply.model_json_schema(),
                    strict=True,
                ),
            ),
        )
        content = resp.choices[0].message.content
        if not content:
            return "unsure"
        return ConfirmationReply.model_validate_json(content).decision
    except Exception as err:  # noqa: BLE001 - classifier must never block routing
        logger.warning("[confirm LLM] falling back to unsure: %s", err)
        return "unsure"

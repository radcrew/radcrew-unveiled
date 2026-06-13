"""NeMo Guardrails integration: input and output rail entry points."""
from __future__ import annotations

import dataclasses
import logging
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

from nemoguardrails import LLMRails, RailsConfig

from app.chatbot.guardrails.hf_llm_adapter import (
    SENTINEL,
    SentinelLLM,
    check_groundedness,
    check_harmful_input,
)
from app.chatbot.knowledge.models import KnowledgeDocument

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path(__file__).parent / "config"

_HARMFUL_INPUT_RESPONSE = "I'm not able to help with that."

_GROUNDEDNESS_FALLBACK = (
    "I don't have enough reliable information to answer that accurately. "
    "Feel free to reach the team at code@radcrew.org."
)


@dataclasses.dataclass(frozen=True)
class RailResult:
    blocked: bool
    response: str = ""


@lru_cache(maxsize=1)
def _rails() -> LLMRails:
    config = RailsConfig.from_path(str(_CONFIG_DIR))
    return LLMRails(config, llm=SentinelLLM())


def apply_input_rail(message: str) -> RailResult:
    """Run NeMo input rails then a harmful-content check against the user message.

    Order matters for cost:
    1. Colang pattern-matched flows (jailbreak, off-topic) — no HuggingFace call.
    2. Only if all patterns pass: HuggingFace harmful-content classifier.

    Both stages fail-open so a transient error never silences a legitimate question.
    """
    try:
        response = _rails().generate(
            messages=[{"role": "user", "content": message}]
        )
        if response.strip() != SENTINEL:
            return RailResult(blocked=True, response=response)
    except Exception:
        logger.exception("[guardrail] NeMo input rail check failed — continuing")

    if check_harmful_input(message):
        logger.info("[guardrail] harmful input blocked message=%r", message[:120])
        return RailResult(blocked=True, response=_HARMFUL_INPUT_RESPONSE)

    return RailResult(blocked=False)


def apply_output_rail_stream(
    stream: Iterator[str],
    context_chunks: list[KnowledgeDocument],
) -> Iterator[str]:
    """Buffer the answer stream, run a groundedness check, then re-yield.

    If the HuggingFace model decides the answer is not grounded in the
    retrieved context chunks, a safe fallback message is yielded instead.
    On any inference failure the original answer is returned as-is so a
    transient error never silences a correct response.
    """
    full_answer = "".join(stream)

    context_text = "\n".join(
        f"({chunk.title}): {chunk.text}" for chunk in context_chunks
    )

    try:
        grounded = check_groundedness(full_answer, context_text)
    except Exception:
        logger.exception("[guardrail] output rail check failed — returning answer as-is")
        grounded = True

    if not grounded:
        logger.warning("[guardrail] output grounding check failed — returning fallback")
        yield _GROUNDEDNESS_FALLBACK
        return

    yield full_answer

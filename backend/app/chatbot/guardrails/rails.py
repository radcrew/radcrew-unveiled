"""NeMo Guardrails integration: input and output rail entry points."""
from __future__ import annotations

import dataclasses
import logging
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

from app.chatbot.guardrails.hf_llm_adapter import (
    SENTINEL,
    SentinelLLM,
    check_groundedness,
    check_harmful_input,
    scrub_pii_output,
    scrub_pii_stream,
)
from app.chatbot.knowledge.models import KnowledgeDocument
from app.core.settings import get_settings

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
def _rails():  # -> LLMRails (imported lazily to avoid hard dep at import time)
    from nemoguardrails import LLMRails, RailsConfig

    config = RailsConfig.from_path(str(_CONFIG_DIR))
    return LLMRails(config, llm=SentinelLLM())


def apply_input_rail(message: str) -> RailResult:
    """Run NeMo input rails then a harmful-content check against the user message.

    Each stage is controlled by a feature flag in settings:
    1. GUARDRAIL_INPUT_PATTERNS_ENABLED — Colang jailbreak/off-topic patterns (no HF call).
    2. GUARDRAIL_INPUT_HARMFUL_ENABLED  — HF harmful-content classifier (one HF call).

    Both stages fail-open so a transient error never silences a legitimate question.
    """
    settings = get_settings()

    if settings.GUARDRAIL_INPUT_PATTERNS_ENABLED:
        try:
            response = _rails().generate(
                messages=[{"role": "user", "content": message}]
            )
            if response.strip() != SENTINEL:
                return RailResult(blocked=True, response=response)
        except Exception:
            logger.exception("[guardrail] NeMo input rail check failed — continuing")

    if settings.GUARDRAIL_INPUT_HARMFUL_ENABLED and check_harmful_input(message):
        logger.info("[guardrail] harmful input blocked message=%r", message[:120])
        return RailResult(blocked=True, response=_HARMFUL_INPUT_RESPONSE)

    return RailResult(blocked=False)


def apply_output_rail_stream(
    stream: Iterator[str],
    context_chunks: list[KnowledgeDocument],
) -> Iterator[str]:
    """Apply output guardrails controlled by feature flags in settings.

    GUARDRAIL_OUTPUT_GROUNDEDNESS_ENABLED — buffers the full answer, asks the
      HF model whether it is grounded in the retrieved chunks, and replaces an
      ungrounded answer with a safe fallback. Requires one extra HF call.

    GUARDRAIL_OUTPUT_PII_ENABLED — redacts phone numbers. When groundedness is
      disabled this runs as a streaming transform (no buffering, no extra HF
      call). When groundedness is enabled the PII scrub is applied to the
      buffered text before yielding.
    """
    settings = get_settings()
    pii = settings.GUARDRAIL_OUTPUT_PII_ENABLED
    groundedness = settings.GUARDRAIL_OUTPUT_GROUNDEDNESS_ENABLED

    if not groundedness:
        # Fast path: no buffering required.
        yield from (scrub_pii_stream(stream) if pii else stream)
        return

    # Groundedness check requires the full answer up front.
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

    yield scrub_pii_output(full_answer) if pii else full_answer

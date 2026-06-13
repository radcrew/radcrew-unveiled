"""LangChain-compatible LLM wrappers used by NeMo Guardrails rail instances."""
from __future__ import annotations

import re
from collections.abc import Iterator

from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import Generation, LLMResult

from app.chatbot.huggingface import generate_answer

# ---------------------------------------------------------------------------
# PII patterns
# Matches common phone number formats (US and international) while avoiding
# false positives on version strings, years, or zip codes.
# A separator (space / dash / dot) between the digit groups is required so
# bare 10-digit runs like "2024123456" are not caught.
# ---------------------------------------------------------------------------
_PHONE_RE = re.compile(
    r"""
    (?<!\d)              # not preceded by a digit
    (?:
        \+?\d{1,3}       # optional country code: +1, +44, +61 …
        [\s.\-]          # separator after country code
    )?
    [\(\[]?              # optional opening paren/bracket for area code
    \d{2,4}              # area code or first block
    [\)\]]?              # optional closing paren/bracket
    [\s.\-]              # separator (required — prevents matching bare numbers)
    \d{2,4}              # second block
    [\s.\-]              # separator
    \d{4}                # final four digits
    (?!\d)               # not followed by a digit
    """,
    re.VERBOSE,
)
_PHONE_PLACEHOLDER = "[phone]"

# Returned by SentinelLLM when no input rail pattern matches — tells
# apply_input_rail that the message passed all checks cleanly.
SENTINEL = "__RAIL_PASS__"

_GROUNDEDNESS_SYSTEM = (
    "You are a factual grounding checker. "
    "You only answer with 'yes' or 'no'."
)
_GROUNDEDNESS_PROMPT = (
    "Context sources:\n{context}\n\n"
    "Bot response:\n{answer}\n\n"
    "Is every claim in the bot response directly supported by the context sources? "
    "Answer with only 'yes' or 'no'."
)

_HARMFUL_SYSTEM = (
    "You are a content safety classifier. "
    "You only answer with 'yes' or 'no'."
)
_HARMFUL_PROMPT = (
    "Is the following user message harmful, abusive, illegal, or sexually explicit?\n\n"
    "Message: {message}\n\n"
    "Answer with only 'yes' or 'no'."
)


class SentinelLLM(BaseLLM):
    """Stub that returns SENTINEL as the main LLM response.

    Pattern-matched Colang flows resolve before NeMo ever calls the main LLM,
    so this only fires when no input rail matched — signalling a clean pass.
    """

    @property
    def _llm_type(self) -> str:
        return "sentinel-stub"

    def _call(self, prompt: str, stop: list[str] | None = None, **_: object) -> str:
        return SENTINEL

    def _generate(
        self, prompts: list[str], stop: list[str] | None = None, **_: object
    ) -> LLMResult:
        return LLMResult(
            generations=[[Generation(text=SENTINEL)] for _ in prompts]
        )


def scrub_pii_stream(stream: Iterator[str]) -> Iterator[str]:
    """Apply PII scrubbing per line so it works directly on a token stream.

    Phone numbers never span newlines, so line-by-line processing is safe and
    avoids buffering the entire answer before yielding.
    """
    buffer = ""
    for chunk in stream:
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            yield _PHONE_RE.sub(_PHONE_PLACEHOLDER, line) + "\n"
    if buffer:
        yield _PHONE_RE.sub(_PHONE_PLACEHOLDER, buffer)


def scrub_pii_output(text: str) -> str:
    """Replace phone numbers in the bot response with a placeholder.

    The knowledge base contains team-member profiles that may include personal
    phone numbers. This ensures they are never echoed back to end users.
    Email scrubbing is already handled upstream by sanitize_answer_stream.
    """
    return _PHONE_RE.sub(_PHONE_PLACEHOLDER, text)


def check_harmful_input(message: str) -> bool:
    """Ask the HuggingFace model whether the user message is harmful.

    Returns True when the message should be blocked, False when it is safe.
    Defaults to False (safe) on any inference failure so a transient error
    never silences a legitimate question.
    """
    prompt = _HARMFUL_PROMPT.format(message=message)
    try:
        result = "".join(
            generate_answer(system=_HARMFUL_SYSTEM, user=prompt, history=[])
        )
        return "yes" in result.strip().lower()
    except Exception:
        return False


def check_groundedness(answer: str, context: str) -> bool:
    """Ask the HuggingFace model whether the answer is grounded in the context.

    Returns True (grounded / safe to return) or False (hallucination suspected).
    Defaults to True on any inference failure so a transient error never
    silences a correct answer.
    """
    prompt = _GROUNDEDNESS_PROMPT.format(context=context, answer=answer)
    try:
        result = "".join(
            generate_answer(system=_GROUNDEDNESS_SYSTEM, user=prompt, history=[])
        )
        return "no" not in result.strip().lower()
    except Exception:
        return True

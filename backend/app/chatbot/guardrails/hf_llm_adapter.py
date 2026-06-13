"""LangChain-compatible LLM wrappers used by NeMo Guardrails rail instances."""
from __future__ import annotations

from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import Generation, LLMResult

from app.chatbot.huggingface import generate_answer

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

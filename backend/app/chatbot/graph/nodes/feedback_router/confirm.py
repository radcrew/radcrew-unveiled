"""Confirmation detection for the feedback send flow (Solution D).

Feedback is not sent on first detection. The handler asks the user to confirm;
on the next turn these helpers decide whether the reply is a yes (send), a no
(cancel), or neither (treat as a new message — safe default, nothing sent).

Matching is layered so the common case stays fast and free:
  1. known yes/no phrases ("go ahead", "never mind"),
  2. exact lookup of the first token (covers terse replies "y", "k", "n"),
  3. typo-tolerant lookup via :mod:`fuzzy` for longer tokens ("definitley"),
  4. an LLM fallback in the router (:mod:`confirm_llm`) for anything still
     ambiguous — see :func:`classify_confirmation`.
"""

from __future__ import annotations

import re
from typing import Literal

from .fuzzy import fuzzy_in

Decision = Literal["yes", "no", "unknown"]

_AFFIRMATIONS = frozenset(
    {
        # terse / single-token
        "y", "ya", "yea", "yeh", "ye", "k", "kk",
        # words
        "yes", "yeah", "yep", "yup", "yessir", "sure", "ok", "okay", "okey",
        "confirm", "confirmed", "absolutely", "definitely", "send", "forward",
    }
)
_AFFIRMATION_PHRASES = (
    "go ahead", "send it", "do it", "please do", "please send", "forward it",
    "sounds good", "sure thing", "yes please", "go for it", "lets do it",
)

_NEGATIONS = frozenset(
    {
        # terse / single-token
        "n", "nah", "nay", "nope", "nvm",
        # words
        "no", "cancel", "stop", "dont", "not", "never",
    }
)
_NEGATION_PHRASES = (
    "do not", "never mind", "nevermind", "no thanks", "not now",
    "no thank you", "forget it", "leave it",
)


def _normalize(message: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", "", message.lower())).strip()


def _first_word(text: str) -> str:
    return text.split(" ", 1)[0]


def is_affirmation(message: str) -> bool:
    text = _normalize(message)
    if not text:
        return False
    if any(text.startswith(phrase) for phrase in _AFFIRMATION_PHRASES):
        return True
    return fuzzy_in(_first_word(text), _AFFIRMATIONS)


def is_negation(message: str) -> bool:
    text = _normalize(message)
    if not text:
        return False
    if any(text.startswith(phrase) for phrase in _NEGATION_PHRASES):
        return True
    return fuzzy_in(_first_word(text), _NEGATIONS)


def classify_confirmation(message: str) -> Decision:
    """Deterministic yes/no/unknown for a reply to the confirm prompt.

    A reply that reads as *both* yes and no (a token sitting near two
    vocabularies) is reported as ``unknown`` so the caller defers to the LLM
    rather than guessing and possibly sending something the user did not intend.
    """
    yes = is_affirmation(message)
    no = is_negation(message)
    if yes and not no:
        return "yes"
    if no and not yes:
        return "no"
    return "unknown"

"""Confirmation detection for the feedback send flow (Solution D).

Feedback is not sent on first detection. The handler asks the user to confirm;
on the next turn these helpers decide whether the reply is a yes (send), a no
(cancel), or neither (treat as a new message — safe default, nothing sent).
"""

from __future__ import annotations

import re

_AFFIRMATIONS = frozenset(
    {"yes", "yeah", "yep", "yup", "sure", "ok", "okay", "confirm", "confirmed",
     "absolutely", "definitely", "send", "forward"}
)
_AFFIRMATION_PHRASES = (
    "go ahead", "send it", "do it", "please do", "please send", "forward it",
    "sounds good", "sure thing", "yes please",
)

_NEGATIONS = frozenset(
    {"no", "nope", "nah", "cancel", "stop", "dont", "not", "never"}
)
_NEGATION_PHRASES = (
    "do not", "never mind", "nevermind", "no thanks", "not now", "no thank you",
)


def _normalize(message: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", "", message.lower())).strip()


def is_affirmation(message: str) -> bool:
    text = _normalize(message)
    if not text:
        return False
    if text.split(" ")[0] in _AFFIRMATIONS:
        return True
    return any(text.startswith(phrase) for phrase in _AFFIRMATION_PHRASES)


def is_negation(message: str) -> bool:
    text = _normalize(message)
    if not text:
        return False
    if text.split(" ")[0] in _NEGATIONS:
        return True
    return any(text.startswith(phrase) for phrase in _NEGATION_PHRASES)

"""Deterministic pre-gate for intent routing (Solution A).

Most chat inputs are unambiguous questions. Deciding those in code keeps them
away from the weak 1.5B LLM classifier, which over-classifies questions as
feedback submissions. Only genuinely ambiguous or feedback-signalling messages
fall through to the LLM.

Rule: a clear question with no explicit feedback signal → RAG (skip the LLM).
Everything else → consult the LLM (existing behaviour).
"""

from __future__ import annotations

import re

from .fuzzy import fuzzy_in

# First word (or a trailing "?") that marks a message as a question or an
# information request — these should be answered, never treated as feedback.
_QUESTION_STARTERS = frozenset(
    {
        "who", "what", "when", "where", "why", "how", "which", "whose", "whom",
        "is", "are", "was", "were", "am",
        "do", "does", "did",
        "can", "could", "should", "would", "will", "shall", "may", "might",
        "has", "have", "had",
        # information-request imperatives
        "tell", "explain", "describe", "list", "show", "give", "define",
        "summarize", "summarise", "name",
        # common contractions (apostrophe kept by the tokenizer below)
        "what's", "who's", "where's", "when's", "why's", "how's", "whats",
        "whos", "hows",
    }
)

# Explicit signals that the user wants to send something to the team. Presence
# of any of these makes a message ambiguous enough to defer to the LLM, even if
# it is phrased as a question.
_FEEDBACK_SIGNALS = (
    "feedback",
    "report a bug",
    "report a problem",
    "report an issue",
    "bug report",
    "i want to report",
    "i'd like to report",
    "suggestion",
    "i suggest",
    "i'd suggest",
    "complaint",
    "complain",
    "message to the team",
    "send a message",
    "contact the team",
    "tell the team",
    "let the team know",
    "leave a message",
    "i want to tell you",
)

_FIRST_WORD_RE = re.compile(r"[a-z']+")

# Pure greetings / chit-chat. These are not questions and match no knowledge
# base content, so without special handling they fall straight into the
# low-context fallback. Detected here so they can be answered conversationally
# instead. Kept deliberately tight: a message must consist *only* of these
# tokens (or be an exact small-talk phrase) so "hi, what does RadCrew do?"
# still routes to RAG.
_GREETING_TOKENS = frozenset(
    {
        "hi", "hello", "hey", "heya", "hiya", "yo", "sup", "howdy", "greetings",
        "hii", "helo", "gm",
        "there",
        "good", "morning", "afternoon", "evening", "night",
        "thanks", "thank", "thx", "ty", "cheers", "appreciate", "appreciated",
        "ok", "okay", "kk", "cool", "nice", "great", "awesome", "gotcha",
        "bye", "goodbye", "cya", "later",
        "you", "u",
    }
)

_SMALLTALK_PHRASES = frozenset(
    {
        "thank you", "thanks a lot", "thank you so much", "much appreciated",
        "good morning", "good afternoon", "good evening", "good night",
        "good day", "how are you", "hows it going", "how is it going",
        "whats up", "nice to meet you", "sounds good", "have a good one",
        "see you", "see you later",
    }
)

_SMALLTALK_PUNCT_RE = re.compile(r"[^\w\s]")


def is_smalltalk(message: str) -> bool:
    """True when the message is purely a greeting or other small talk.

    Strips punctuation/apostrophes, then matches either a known small-talk
    phrase or a short message composed entirely of greeting tokens. A message
    that mixes a greeting with a real question (e.g. "hi, who is on the team?")
    fails the all-tokens check and falls through to normal routing.
    """
    text = message.strip().lower().replace("'", "")
    text = " ".join(_SMALLTALK_PUNCT_RE.sub(" ", text).split())
    if not text:
        return False
    if text in _SMALLTALK_PHRASES:
        return True
    tokens = text.split()
    if len(tokens) > 5:
        return False
    return all(token in _GREETING_TOKENS for token in tokens)


def looks_like_question(message: str) -> bool:
    text = message.strip().lower()
    if not text:
        return False
    if text.endswith("?"):
        return True
    match = _FIRST_WORD_RE.match(text)
    if not match:
        return False
    word = match.group(0)
    # Exact, then a tight (single-edit) typo tolerance so "waht"/"explian" still
    # read as questions. Capped at distance 1 because this gate sees open-ended
    # first messages — a looser budget would misroute feedback to RAG.
    return word in _QUESTION_STARTERS or fuzzy_in(
        word, _QUESTION_STARTERS, max_distance=1
    )


def has_feedback_signal(message: str) -> bool:
    text = message.lower()
    return any(signal in text for signal in _FEEDBACK_SIGNALS)


def should_skip_llm_route_to_rag(message: str) -> bool:
    """True when the message is a plain question or small talk, with no feedback signal.

    Both go straight to RAG, bypassing the over-eager LLM classifier (and the
    extra inference call it costs). Anything carrying a feedback signal still
    defers to the LLM so genuine submissions are not lost.
    """
    if has_feedback_signal(message):
        return False
    return looks_like_question(message) or is_smalltalk(message)

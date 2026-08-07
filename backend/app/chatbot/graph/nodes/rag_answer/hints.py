"""Follow-up questions offered under an answer ("hint next steps").

Hints are curated per knowledge document rather than generated, so producing
them costs no inference call and adds no latency to a request that already
makes up to three (router, harmful-input rail, groundedness rail). They are our
own fixed strings, never model output, so they carry no URLs and need no output
rail.

Selection reads the *retrieved* documents, not the context passed to the prompt:
``rag_answer_node`` hands the whole corpus to the model as context, so only the
retrieved list reflects what was actually asked.

Documents with no catalog entry (team profiles loaded from GitHub, whose ids are
``github:<path>``) contribute nothing; their titles come from Markdown headings
and would template into nonsense. The default hints top up whatever is short,
so ``build_hints([], ...)`` is also the right call for paths with no retrieval
at all, such as small talk.
"""

from __future__ import annotations

import re

from app.chatbot.knowledge.models import KnowledgeDocument
from app.schemas import ChatHistoryMessage

# Chips render in a 360px panel, so hints stay short enough to sit on one line.
MAX_HINTS = 3

HINT_CATALOG: dict[str, tuple[str, ...]] = {
    "hero": (
        "What kind of products do you build?",
        "How big is the team?",
    ),
    "services": (
        "Can you add AI to an existing product?",
        "Do you do smart contract work?",
    ),
    "services-specialist": (
        "Do you audit smart contracts?",
        "Can you join our existing team?",
    ),
    "how-we-work": (
        "What happens after launch?",
        "How do you run a build phase?",
    ),
    "stats": (
        "How long has RadCrew been building?",
        "What kind of clients do you work with?",
    ),
    "portfolio": (
        "Tell me about CryptoPets.",
        "What was the real estate project?",
    ),
    "tech-stack": (
        "Which frontend stack do you use?",
        "Do you work with Rust?",
    ),
    "testimonial": (
        "What kind of clients do you work with?",
        "What makes RadCrew different?",
    ),
    "clients": (
        "What kind of clients do you work with?",
        "What makes RadCrew different?",
    ),
    "case-study-spotlight": (
        "What results have you delivered?",
        "How long does a project take?",
    ),
    "journal": (
        "What do you write about?",
        "Tell me about your AI work.",
    ),
    "faq": (
        "How quickly can you start?",
        "Do you offer post-launch support?",
    ),
    "faq-working-together": (
        "Can you work in our existing codebase?",
        "What happens if we need to stop?",
    ),
    "contact": (
        "How do I start a project?",
        "How fast do you reply?",
    ),
    "social-links": (
        "Where can I see your code?",
        "How do I get in touch?",
    ),
}

DEFAULT_HINTS: tuple[str, ...] = (
    "What does RadCrew build?",
    "How do I start a project?",
    "How quickly can you start?",
)

_WORD_RE = re.compile(r"[a-z0-9]+")


def _normalize(text: str) -> str:
    """Lowercase word sequence, so punctuation and casing don't defeat matching."""
    return " ".join(_WORD_RE.findall(text.lower()))


def build_hints(
    retrieved_documents: list[KnowledgeDocument],
    message: str,
    history: list[ChatHistoryMessage] | None = None,
) -> tuple[str, ...]:
    """Up to ``MAX_HINTS`` follow-ups for what was just retrieved.

    Hints the user has already asked are dropped, so the chips never offer back
    the question that produced the answer they are sitting under. That can leave
    fewer than ``MAX_HINTS``, which is the honest outcome: better a short row
    than a redundant one.
    """
    asked = [_normalize(m.content) for m in (history or []) if m.role == "user"]
    asked.append(_normalize(message))

    candidates = [
        hint
        for document in retrieved_documents
        for hint in HINT_CATALOG.get(document.id, ())
    ]
    candidates += DEFAULT_HINTS

    hints: list[str] = []
    for hint in candidates:
        if hint in hints:
            continue
        normalized = _normalize(hint)
        if any(normalized in asked_text for asked_text in asked):
            continue
        hints.append(hint)
        if len(hints) == MAX_HINTS:
            break
    return tuple(hints)

"""Deep search: a web-search fallback for questions the static KB can't answer.

Used only when knowledge-base retrieval is weak (see the RAG answer node). The
fallback is inert until ``WEB_SEARCH_API_KEY`` is configured, so deployments
without a search provider keep working exactly as before.
"""

from __future__ import annotations

from app.chatbot.deepsearch.web_search import deep_search_documents, is_deep_search_available

__all__ = [
    "deep_search_documents",
    "is_deep_search_available",
]

"""Web-search provider for deep search (stdlib only, no extra dependencies).

Currently implements Tavily (https://tavily.com), a search API designed for LLM
apps that returns clean text snippets. The provider is selected by
``WEB_SEARCH_PROVIDER`` and authenticated with ``WEB_SEARCH_API_KEY``. Any
failure (no key, network error, bad response) degrades to an empty result list
so the chatbot falls back to its normal "not enough information" answer rather
than erroring.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from app.chatbot.knowledge.models import KnowledgeDocument
from app.chatbot.utils.documents import (
    DEFAULT_SEARCH_RESULT_MAX_CHARS,
    search_results_to_documents,
)
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

_TAVILY_ENDPOINT = "https://api.tavily.com/search"
_REQUEST_TIMEOUT_SECONDS = 8


def is_deep_search_available() -> bool:
    """True when deep search is enabled and a provider key is configured."""
    settings = get_settings()
    return bool(settings.DEEP_SEARCH_ENABLED and settings.WEB_SEARCH_API_KEY)


def deep_search_documents(query: str) -> list[KnowledgeDocument]:
    """Run a web search for ``query`` and return results as KnowledgeDocuments.

    Returns an empty list when deep search is unavailable or the search fails.
    """
    if not query.strip() or not is_deep_search_available():
        return []

    settings = get_settings()
    provider = settings.WEB_SEARCH_PROVIDER.lower().strip()

    try:
        if provider == "tavily":
            return _search_tavily(
                query,
                api_key=settings.WEB_SEARCH_API_KEY or "",
                max_results=settings.WEB_SEARCH_MAX_RESULTS,
            )
        logger.error("[deepsearch] unknown WEB_SEARCH_PROVIDER=%r", provider)
        return []
    except (urllib.error.URLError, TimeoutError, ValueError) as err:
        logger.error("[deepsearch provider=%s] %s", provider, err)
        return []
    except Exception as err:  # never let search break the answer path
        logger.exception("[deepsearch provider=%s] unexpected error: %s", provider, err)
        return []


def _search_tavily(query: str, api_key: str, max_results: int) -> list[KnowledgeDocument]:
    payload = json.dumps(
        {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": False,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        _TAVILY_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        body = json.loads(response.read().decode("utf-8"))

    return search_results_to_documents(
        body.get("results", []),
        max_text_chars=DEFAULT_SEARCH_RESULT_MAX_CHARS,
    )

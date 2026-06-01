"""Map provider search API payloads to ``KnowledgeDocument`` records."""

from __future__ import annotations

from app.chatbot.knowledge.models import KnowledgeDocument

DEFAULT_SEARCH_RESULT_MAX_CHARS = 600


def search_results_to_documents(
    results: object,
    *,
    id_prefix: str = "web",
    max_text_chars: int = DEFAULT_SEARCH_RESULT_MAX_CHARS,
    default_title: str = "Web result",
) -> list[KnowledgeDocument]:
    """Convert a list of ``{title, content, url}`` dicts into knowledge documents."""
    if not isinstance(results, list):
        return []

    documents: list[KnowledgeDocument] = []
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            continue
        content = (result.get("content") or "").strip()
        title = (result.get("title") or "").strip()
        if not content:
            continue
        if len(content) > max_text_chars:
            content = content[:max_text_chars].rstrip() + "…"
        url = result.get("url") if isinstance(result.get("url"), str) else None
        documents.append(
            KnowledgeDocument(
                id=f"{id_prefix}-{index}",
                title=title or default_title,
                text=content,
                url=url,
            )
        )
    return documents

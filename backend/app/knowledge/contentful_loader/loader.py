"""Orchestrate Contentful → KnowledgeDocument for startup RAG ingestion."""

from __future__ import annotations

import json
import logging
from urllib.error import HTTPError, URLError

from app.knowledge.contentful_loader.api import fetch_contentful_entries
from app.knowledge.contentful_loader.mapping import map_generic_entry
from app.knowledge.models import KnowledgeDocument

logger = logging.getLogger(__name__)


def get_contentful_documents(
    *,
    space_id: str | None,
    access_token: str | None,
    environment: str,
    content_types_csv: str,
) -> list[KnowledgeDocument]:
    """Load knowledge documents from Contentful when space and token are set."""
    if not (space_id or "").strip():
        return []
    if not (access_token or "").strip():
        return []

    raw_types = [t.strip() for t in content_types_csv.split(",") if t.strip()]
    if not raw_types:
        return []

    env = environment.strip() or "master"
    documents: list[KnowledgeDocument] = []

    for ct in raw_types:
        try:
            entries = fetch_contentful_entries(
                space_id=space_id.strip(),
                access_token=access_token.strip(),
                environment=env,
                content_type=ct,
                order=None,
            )
            for entry in entries:
                documents.append(map_generic_entry(entry, ct))
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("Contentful KB ingestion failed for content_type=%s: %s", ct, exc)

    return documents

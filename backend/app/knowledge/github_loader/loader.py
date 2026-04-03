from __future__ import annotations

import json
import logging
from urllib import parse
from urllib.error import HTTPError, URLError

from app.knowledge.github_loader.api import API_BASE, get_json
from app.knowledge.github_loader.decoder import decode_blob_content
from app.knowledge.github_loader.parsing import (
    is_markdown_file,
    parse_repo_source_url,
    title_from_markdown,
)
from app.knowledge.models import KnowledgeDocument

logger = logging.getLogger(__name__)


def get_github_markdown_documents(
    *,
    repo_url: str | None,
    token: str | None,
    branch: str | None = None,
    path_prefix: str | None = None,
) -> list[KnowledgeDocument]:
    """Fetch markdown files from a GitHub repo and return knowledge documents.

    Returns an empty list when source config is missing or any API call fails.
    """
    if not repo_url:
        return []

    if branch is None or not (branch := branch.strip()):
        logger.warning("Skipping GitHub KB ingestion: branch is required when repo_url is set")
        return []

    try:
        repo_source = parse_repo_source_url(repo_url)
    except ValueError as exc:
        logger.warning("Skipping GitHub KB ingestion, invalid repo URL: %s", exc)
        return []

    try:
        tree_payload = get_json(
            f"{API_BASE}/repos/{repo_source.owner}/{repo_source.repo}/git/trees/{parse.quote(branch)}?recursive=1",
            token=token,
        )
        tree_items = tree_payload.get("tree", [])
        if not isinstance(tree_items, list):
            logger.warning("GitHub tree response has unexpected shape for repo %s", repo_url)
            return []

        documents: list[KnowledgeDocument] = []
        for entry in tree_items:
            if not isinstance(entry, dict):
                continue
            if entry.get("type") != "blob":
                continue
            blob_path = str(entry.get("path") or "")
            if not blob_path or not is_markdown_file(blob_path):
                continue
            if path_prefix and not blob_path.startswith(path_prefix):
                continue
            sha = str(entry.get("sha") or "")
            if not sha:
                continue

            blob_payload = get_json(
                f"{API_BASE}/repos/{repo_source.owner}/{repo_source.repo}/git/blobs/{sha}",
                token=token,
            )
            text = decode_blob_content(blob_payload)
            if not text.strip():
                continue

            documents.append(
                KnowledgeDocument(
                    id=f"github:{blob_path}",
                    title=title_from_markdown(blob_path, text),
                    text=text,
                    url=f"https://{repo_source.host}/{repo_source.owner}/{repo_source.repo}/blob/{branch}/{blob_path}",
                )
            )
        return documents
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        logger.warning("GitHub KB ingestion failed for %s: %s", repo_url, exc)
        return []

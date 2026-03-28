"""Contentful Delivery API loader (parity with backend/src/knowledge/contentful-loader.ts)."""

from __future__ import annotations

import json
from typing import Any, cast

import httpx

from app.config import Settings
from app.models import KnowledgeDocument

_CONTENTFUL_CDN = "https://cdn.contentful.com"


def _pick_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for part in value.values():
            if isinstance(part, str):
                return part
        return ""
    return str(value)


def _fields_to_text(fields: dict[str, Any]) -> str:
    parts: list[str] = []
    for field in fields.values():
        s = _pick_string(field).strip()
        if s:
            parts.append(s)
    return " ".join(parts)


def _parse_entries_payload(data: dict[str, Any]) -> list[KnowledgeDocument]:
    items = data.get("items")
    if not isinstance(items, list):
        return []

    space_id = data.get("_space_id")
    if not isinstance(space_id, str):
        space_id = ""

    out: list[KnowledgeDocument] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        sys_obj = raw.get("sys")
        entry_id = ""
        if isinstance(sys_obj, dict):
            eid = sys_obj.get("id")
            if isinstance(eid, str):
                entry_id = eid

        fields_raw = raw.get("fields")
        if not isinstance(fields_raw, dict):
            continue
        fields = cast(dict[str, Any], fields_raw)

        text = _fields_to_text(fields)
        if not text:
            continue

        title = (
            _pick_string(fields.get("title"))
            or _pick_string(fields.get("name"))
            or _pick_string(fields.get("heading"))
            or f"Contentful entry {entry_id}"
        )

        url = (
            f"https://app.contentful.com/spaces/{space_id}/entries/{entry_id}"
            if space_id and entry_id
            else None
        )

        out.append(
            KnowledgeDocument(
                id=f"contentful:{entry_id}",
                title=title,
                text=text,
                url=url,
            )
        )
    return out


async def load_contentful_documents(config: Settings) -> list[KnowledgeDocument]:
    if not config.CONTENTFUL_SPACE_ID or not config.CONTENTFUL_DELIVERY_TOKEN:
        return []

    space_id = config.CONTENTFUL_SPACE_ID.strip()
    env = config.CONTENTFUL_ENVIRONMENT.strip() or "master"
    url = f"{_CONTENTFUL_CDN}/spaces/{space_id}/environments/{env}/entries"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            url,
            params={"limit": 100, "include": 0},
            headers={"Authorization": f"Bearer {config.CONTENTFUL_DELIVERY_TOKEN.strip()}"},
        )
        response.raise_for_status()
        data = response.json()

    if not isinstance(data, dict):
        return []

    # stash space id for entry URLs (same pattern as Node template string)
    data = dict(data)
    data["_space_id"] = space_id

    return _parse_entries_payload(data)


def parse_contentful_entries_json(json_text: str, space_id: str) -> list[KnowledgeDocument]:
    """Parse a Contentful entries JSON body (for tests and debugging)."""
    data = json.loads(json_text)
    if not isinstance(data, dict):
        return []
    payload = dict(cast(dict[str, Any], data))
    payload["_space_id"] = space_id
    return _parse_entries_payload(payload)

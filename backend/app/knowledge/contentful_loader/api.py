"""Content Delivery API HTTP client (paginated entry fetch)."""

from __future__ import annotations

import json
from urllib import parse, request

from app.knowledge.contentful_loader.constants import CDN_BASE, USER_AGENT


def cdn_get_json(path: str, params: dict[str, str]) -> dict[str, object]:
    qs = parse.urlencode(params)
    url = f"{CDN_BASE}{path}?{qs}"
    req = request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    with request.urlopen(req, timeout=30) as response:
        payload = response.read()
    parsed = json.loads(payload.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("Contentful response must be a JSON object")
    return parsed


def fetch_entries_page(
    *,
    space_id: str,
    access_token: str,
    environment: str,
    content_type: str,
    skip: int,
    limit: int,
    order: str | None,
) -> tuple[list[dict[str, object]], int]:
    path = f"/spaces/{parse.quote(space_id, safe='')}/environments/{parse.quote(environment, safe='')}/entries"
    params: dict[str, str] = {
        "access_token": access_token,
        "content_type": content_type,
        "skip": str(skip),
        "limit": str(limit),
    }
    if order:
        params["order"] = order

    data = cdn_get_json(path, params)

    items_raw = data.get("items")
    if not isinstance(items_raw, list):
        return [], 0

    items: list[dict[str, object]] = [x for x in items_raw if isinstance(x, dict)]

    total_raw = data.get("total")
    total = int(total_raw) if isinstance(total_raw, int) else len(items)

    return items, total


def fetch_contentful_entries(
    *,
    space_id: str,
    access_token: str,
    environment: str,
    content_type: str,
    order: str | None = None,
    page_size: int = 100,
) -> list[dict[str, object]]:
    """Fetch all entries of a content type (paginated)."""
    out: list[dict[str, object]] = []
    skip = 0
    while True:
        items, total = fetch_entries_page(
            space_id=space_id,
            access_token=access_token,
            environment=environment,
            content_type=content_type,
            skip=skip,
            limit=page_size,
            order=order,
        )
        out.extend(items)
        skip += len(items)
        if skip >= total or not items:
            break
    return out

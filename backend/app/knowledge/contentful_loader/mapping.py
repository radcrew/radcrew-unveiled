"""Map Contentful entry JSON to KnowledgeDocument."""

from __future__ import annotations

from urllib import parse

from app.knowledge.contentful_loader.plain_text import field_to_plain
from app.knowledge.models import KnowledgeDocument


def map_generic_entry(entry: dict[str, object], content_type: str) -> KnowledgeDocument:
    sys_obj = entry.get("sys")
    if not isinstance(sys_obj, dict):
        raise ValueError("Entry missing sys")
    entry_id = str(sys_obj.get("id", ""))
    fields_raw = entry.get("fields")
    fields: dict[str, object] = fields_raw if isinstance(fields_raw, dict) else {}

    title = f"{content_type} ({entry_id})"
    for key in ("title", "name", "heading", "headline"):
        t = field_to_plain(fields, key)
        if t:
            title = t
            break

    lines: list[str] = []
    for key in sorted(fields.keys()):
        text = field_to_plain(fields, key)
        if text:
            lines.append(f"{key}: {text}")

    return KnowledgeDocument(
        id=f"contentful:{content_type}:{entry_id}",
        title=title,
        text="\n".join(lines) if lines else title,
        url=None,
    )

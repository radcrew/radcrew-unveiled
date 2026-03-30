"""Plain-text extraction from Contentful Rich Text and localized entry fields."""

from __future__ import annotations


def rich_text_to_plain(node: object) -> str:
    """Extract plain text from a Contentful Rich Text document (minimal walker)."""
    if not isinstance(node, dict):
        return ""
    node_type = node.get("nodeType")
    if node_type == "document":
        parts = [rich_text_to_plain(c) for c in node.get("content", []) if isinstance(c, dict)]
        return " ".join(p for p in parts if p)
    if node_type in ("paragraph", "heading-1", "heading-2", "heading-3", "heading-4", "heading-5", "heading-6"):
        # Inline text nodes usually carry their own spacing (e.g. "Hello" + " world.").
        return "".join(rich_text_to_plain(c) for c in node.get("content", []) if isinstance(c, dict))
    if node_type == "text":
        return str(node.get("value", ""))
    if node_type == "hyperlink":
        return rich_text_to_plain({"content": node.get("content", [])})
    if node_type in ("blockquote", "list-item"):
        return rich_text_to_plain({"content": node.get("content", [])})
    if "content" in node and isinstance(node["content"], list):
        return " ".join(rich_text_to_plain(c) for c in node["content"] if isinstance(c, dict))
    return ""


def _unwrap_localized_field(raw: object) -> object:
    """Return inner value for localized fields; pass through rich text documents."""
    if raw is None:
        return None
    if isinstance(raw, dict) and raw.get("nodeType") == "document":
        return raw
    if isinstance(raw, dict):
        for v in raw.values():
            return v
    return raw


def field_to_plain(fields: dict[str, object], key: str) -> str:
    """String or Rich Text field to plain text."""
    raw = fields.get(key)
    inner = _unwrap_localized_field(raw)
    if inner is None:
        return ""
    if isinstance(inner, str):
        return inner.strip()
    if isinstance(inner, dict) and inner.get("nodeType") == "document":
        return rich_text_to_plain(inner).strip()
    return ""

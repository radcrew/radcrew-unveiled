"""Map Contentful entry JSON to KnowledgeDocument."""

from __future__ import annotations

from urllib import parse

from app.knowledge.contentful_loader.constants import ENGINEERS_CONTENT_TYPE
from app.knowledge.contentful_loader.plain_text import field_to_plain
from app.knowledge.models import KnowledgeDocument


def map_engineer_entry(entry: dict[str, object], site_base_url: str) -> KnowledgeDocument:
    sys_obj = entry.get("sys")
    if not isinstance(sys_obj, dict):
        raise ValueError("Entry missing sys")

    entry_id = str(sys_obj.get("id", ""))
    fields_raw = entry.get("fields")
    if not isinstance(fields_raw, dict):
        fields: dict[str, object] = {}
    else:
        fields = fields_raw

    name = field_to_plain(fields, "name")
    role = field_to_plain(fields, "role")
    bio = field_to_plain(fields, "summery") or field_to_plain(fields, "summary")
    website = field_to_plain(fields, "website")

    title = f"{name} — {role}" if name and role else (name or "RadCrew team member")
    parts: list[str] = []
    if name:
        parts.append(f"Name: {name}")
    if role:
        parts.append(f"Role: {role}")
    if bio:
        parts.append(f"Bio: {bio}")
    if website:
        parts.append(f"Website: {website}")

    if not parts:
        parts.append("No profile details available.")

    path = parse.urljoin(site_base_url.rstrip("/") + "/", f"team/{entry_id}")
    return KnowledgeDocument(
        id=f"contentful:{ENGINEERS_CONTENT_TYPE}:{entry_id}",
        title=title,
        text="\n".join(parts),
        url=path,
    )


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

    # No stable public URL pattern for arbitrary types; engineers use /team/:id above.
    return KnowledgeDocument(
        id=f"contentful:{content_type}:{entry_id}",
        title=title,
        text="\n".join(lines) if lines else title,
        url=None,
    )

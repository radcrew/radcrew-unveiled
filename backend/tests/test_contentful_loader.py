"""Contentful RAG loader: rich text and engineer entry mapping."""

from __future__ import annotations

from app.knowledge.contentful_loader.plain_text import field_to_plain, rich_text_to_plain
from app.knowledge.contentful_loader.mapping import map_engineer_entry


def test_rich_text_to_plain_paragraph() -> None:
    doc = {
        "nodeType": "document",
        "content": [
            {
                "nodeType": "paragraph",
                "content": [
                    {"nodeType": "text", "value": "Hello", "marks": []},
                    {"nodeType": "text", "value": " world.", "marks": []},
                ],
            }
        ],
    }
    assert rich_text_to_plain(doc).strip() == "Hello world."


def test_field_to_plain_localized_string() -> None:
    fields = {"name": {"en-US": "Ada"}}
    assert field_to_plain(fields, "name") == "Ada"


def test_field_to_plain_rich_text_bio() -> None:
    fields = {
        "summery": {
            "en-US": {
                "nodeType": "document",
                "content": [
                    {
                        "nodeType": "paragraph",
                        "content": [{"nodeType": "text", "value": "Builds APIs.", "marks": []}],
                    }
                ],
            }
        }
    }
    assert field_to_plain(fields, "summery") == "Builds APIs."


def test_map_engineer_entry() -> None:
    entry = {
        "sys": {"id": "abc123"},
        "fields": {
            "name": {"en-US": "Ada Lovelace"},
            "role": {"en-US": "Engineer / Founder"},
            "summery": {"en-US": "Focus on reliability."},
            "website": {"en-US": "https://example.com"},
        },
    }
    doc = map_engineer_entry(entry, "http://localhost:8080")
    assert doc.id == "contentful:engineers:abc123"
    assert "Ada Lovelace" in doc.title
    assert "Engineer" in doc.text
    assert "Focus on reliability." in doc.text
    assert doc.url == "http://localhost:8080/team/abc123"

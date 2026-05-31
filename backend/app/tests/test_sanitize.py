"""Deterministic answer guardrail: bullets, links, URLs."""

from __future__ import annotations

from app.chatbot.graph.nodes.rag_answer.sanitize import (
    sanitize_answer_stream,
    sanitize_answer_text,
)


def test_star_bullets_become_dashes() -> None:
    assert sanitize_answer_text("* one\n* two") == "- one\n- two"


def test_indented_star_bullet_keeps_indent() -> None:
    assert sanitize_answer_text("  * nested") == "  - nested"


def test_unicode_bullets_become_dashes() -> None:
    assert sanitize_answer_text("• **Hector**: dev") == "- **Hector**: dev"
    assert sanitize_answer_text("· item") == "- item"


def test_bold_markers_are_left_untouched() -> None:
    assert sanitize_answer_text("**Role:** developer") == "**Role:** developer"
    assert sanitize_answer_text("- **Role:** dev") == "- **Role:** dev"


def test_markdown_link_reduced_to_text() -> None:
    assert sanitize_answer_text("See [the site](https://radcrew.org).") == "See the site."


def test_bare_url_is_stripped() -> None:
    assert sanitize_answer_text("Visit https://radcrew.org now") == "Visit now"


def test_href_attribute_is_stripped() -> None:
    assert sanitize_answer_text('<a href="https://x.com">x</a>') == "<a>x</a>"


def test_stream_reconstructs_sanitized_text() -> None:
    chunks = ["* fir", "st\n", "see [home]", "(https://r.org)\n", "* last"]
    assert "".join(sanitize_answer_stream(iter(chunks))) == "- first\nsee home\n- last"

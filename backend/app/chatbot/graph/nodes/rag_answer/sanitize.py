"""Deterministic guardrail on the model's answer.

The system prompt asks the model to use '-' bullets and to omit URLs/links, but
a small model drifts. These transforms enforce those rules in code instead of
trusting the model. Applied per line so it works on the token stream (lines are
emitted as they complete), and the same logic runs on full text for caching.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

# Leading bullet glyph → "- ". For '*' the trailing whitespace is required so
# bold markers like **label** are left untouched; '•' and '·' are always bullets.
_BULLET_RE = re.compile(r"^(\s*)(?:\*(?=\s)|[•·])(\s*)")
# Markdown link [text](url) → text
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
# href="..." / href='...'
_HREF_RE = re.compile(r"""\s*href\s*=\s*(?:"[^"]*"|'[^']*')""", re.IGNORECASE)
# Bare URLs
_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_WWW_RE = re.compile(r"\bwww\.\S+", re.IGNORECASE)
# Two+ interior spaces (not leading indentation) collapse to one.
_INTERIOR_SPACES_RE = re.compile(r"(?<=\S)[ \t]{2,}")


def _sanitize_line(line: str) -> str:
    line = _BULLET_RE.sub(r"\1-\2", line)
    line = _MD_LINK_RE.sub(r"\1", line)
    line = _HREF_RE.sub("", line)
    line = _URL_RE.sub("", line)
    line = _WWW_RE.sub("", line)
    line = _INTERIOR_SPACES_RE.sub(" ", line)
    return line.rstrip()


def sanitize_answer_text(text: str) -> str:
    return "\n".join(_sanitize_line(line) for line in text.split("\n"))


def sanitize_answer_stream(stream: Iterator[str]) -> Iterator[str]:
    buffer = ""
    for chunk in stream:
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            yield _sanitize_line(line) + "\n"
    if buffer:
        yield _sanitize_line(buffer)

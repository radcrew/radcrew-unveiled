"""Structured tool-call representation from model output."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedToolCall:
    """One model-emitted tool call (OpenAI-style)."""

    id: str
    name: str
    arguments: str

"""Knowledge indexing data shapes (parity with backend/src/types.ts)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeDocument:
    id: str
    title: str
    text: str
    url: str | None = None


@dataclass(frozen=True)
class GithubRepoSource:
    owner: str
    repo: str
    host: str

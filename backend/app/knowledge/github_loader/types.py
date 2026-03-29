from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GithubRepoRef:
    owner: str
    repo: str
    host: str

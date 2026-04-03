from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GithubRepoSource:
    owner: str
    repo: str
    host: str

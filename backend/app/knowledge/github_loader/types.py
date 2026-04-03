from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GithubRepoSource:
    owner: str
    repo: str
    host: str
    inferred_branch: str | None = None
    inferred_path_prefix: str | None = None

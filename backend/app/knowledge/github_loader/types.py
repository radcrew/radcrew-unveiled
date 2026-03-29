from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GithubRepoRef:
    owner: str
    repo: str
    host: str


@dataclass(frozen=True)
class GithubRepoSource:
    repo: GithubRepoRef
    inferred_branch: str | None = None
    inferred_path_prefix: str | None = None

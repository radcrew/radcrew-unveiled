from __future__ import annotations

from pathlib import PurePosixPath
from urllib import parse

from app.knowledge.github_loader.types import GithubRepoRef

_MARKDOWN_SUFFIXES = (".md", ".mdx")


def parse_repo_url(repo_url: str) -> GithubRepoRef:
    parsed = parse.urlparse(repo_url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("repo URL must be http(s)")
    host = parsed.netloc.lower()
    if not host:
        raise ValueError("repo URL is missing host")
    path = parsed.path.strip("/")
    segments = [s for s in path.split("/") if s]
    if len(segments) < 2:
        raise ValueError("repo URL must include owner and repo")
    owner = segments[0]
    repo = segments[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    if not owner or not repo:
        raise ValueError("repo URL must include owner and repo")
    return GithubRepoRef(owner=owner, repo=repo, host=host)


def normalize_path_prefix(path_prefix: str | None) -> str:
    if not path_prefix:
        return ""
    normalized = path_prefix.strip().strip("/")
    return f"{normalized}/" if normalized else ""


def is_markdown_file(file_path: str) -> bool:
    return file_path.lower().endswith(_MARKDOWN_SUFFIXES)


def title_from_path(file_path: str) -> str:
    path = PurePosixPath(file_path)
    stem = path.stem.replace("-", " ").replace("_", " ").strip()
    return stem or file_path

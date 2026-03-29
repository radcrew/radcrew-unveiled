from __future__ import annotations

from pathlib import PurePosixPath
from urllib import parse

from app.knowledge.github_loader.types import GithubRepoRef, GithubRepoSource

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


def parse_repo_source_url(repo_url: str) -> GithubRepoSource:
    parsed = parse.urlparse(repo_url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("repo URL must be http(s)")
    host = parsed.netloc.lower()
    if not host:
        raise ValueError("repo URL is missing host")
    if host != "github.com":
        raise ValueError("repo URL host must be github.com")

    segments = [s for s in parsed.path.strip("/").split("/") if s]
    if len(segments) < 2:
        raise ValueError("repo URL must include owner and repo")

    owner, repo = segments[0], segments[1]
    repo = repo[:-4] if repo.endswith(".git") else repo
    if not owner or not repo:
        raise ValueError("repo URL must include owner and repo")

    inferred_branch: str | None = None
    inferred_path_prefix: str | None = None
    if len(segments) >= 4 and segments[2] in {"tree", "blob"}:
        inferred_branch = segments[3].strip() or None
        inferred_path_prefix = _derive_prefix_from_path_segments(
            segments[4:],
            is_blob_url=segments[2] == "blob",
        )

    return GithubRepoSource(
        repo=GithubRepoRef(owner=owner, repo=repo, host=host),
        inferred_branch=inferred_branch,
        inferred_path_prefix=inferred_path_prefix,
    )


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


def _derive_prefix_from_path_segments(segments: list[str], *, is_blob_url: bool) -> str | None:
    if not segments:
        return None
    if is_blob_url:
        # Blob/raw links usually target a single file. We scope to its parent dir
        # so all markdown files alongside that file are loaded.
        leaf = PurePosixPath(segments[-1])
        scoped_segments = segments[:-1] if leaf.suffix else segments
        if not scoped_segments:
            return None
        return "/".join(scoped_segments)
    return "/".join(segments)

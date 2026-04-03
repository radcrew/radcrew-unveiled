from __future__ import annotations

import re
from pathlib import PurePosixPath
from urllib import parse

from app.knowledge.github_loader.types import GithubRepoSource

_MARKDOWN_SUFFIXES = (".md", ".mdx")
_NAME_LINE_RE = re.compile(r"^\s*(?:real\s+name|name)\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)


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

    inferred_path_prefix: str | None = None
    # Input URLs are expected in form:
    # https://github.com/<owner>/<repo>/tree/<branch>/<directory>
    # Branch comes from settings, so only directory path is inferred.
    if len(segments) >= 5 and segments[2] == "tree":
        inferred_path_prefix = "/".join(segments[4:])

    return GithubRepoSource(
        owner=owner,
        repo=repo,
        host=host,
        inferred_branch=None,
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


def title_from_markdown(file_path: str, markdown_text: str) -> str:
    """Prefer in-content names over filename-derived labels."""
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Team-member markdown convention: first non-empty line is the member name.
        candidate = re.sub(r"^\s*#+\s*", "", line).strip()
        name_match = re.match(r"^(?:real\s+name|name)\s*:\s*(.+?)\s*$", candidate, re.IGNORECASE)
        if name_match:
            candidate = name_match.group(1).strip()
        candidate = candidate.strip("*_`").strip()
        if candidate:
            return candidate
        break

    name_line = _NAME_LINE_RE.search(markdown_text)
    if name_line:
        candidate = name_line.group(1).strip()
        if candidate:
            return candidate

    heading = _H1_RE.search(markdown_text)
    if heading:
        candidate = heading.group(1).strip().strip("#").strip()
        if candidate:
            return candidate

    return title_from_path(file_path)

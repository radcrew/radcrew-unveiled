from __future__ import annotations

from pathlib import PurePosixPath
from urllib import parse

from app.chatbot.knowledge.models import GithubRepoSource

_MARKDOWN_SUFFIXES = (".md", ".mdx")


def parse_repo_source_url(repo_url: object) -> GithubRepoSource:
    url = str(repo_url).strip()
    parsed = parse.urlparse(url)
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

    return GithubRepoSource(owner=owner, repo=repo, host=host)


def is_markdown_file(file_path: str) -> bool:
    return file_path.lower().endswith(_MARKDOWN_SUFFIXES)


def title_from_path(file_path: str) -> str:
    path = PurePosixPath(file_path)
    stem = path.stem.replace("-", " ").replace("_", " ").strip()
    return stem or file_path


def title_from_markdown(file_path: str, markdown_text: str) -> str:
    text = markdown_text.lstrip("\ufeff")

    lines = text.splitlines()
    if not lines:
        return title_from_path(file_path)

    line = lines[0].strip()
    if line.startswith("#"):
        name = line[1:].lstrip()
        if name:
            return name

    return title_from_path(file_path)

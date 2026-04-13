from __future__ import annotations

import base64
from urllib.error import HTTPError

from app.chatbot.knowledge.github_loader.loader import get_resume_documents


def test_github_loader_returns_markdown_documents(monkeypatch):
    blob_text = "# Guide\n\nPrivate repo setup details."
    encoded_blob = base64.b64encode(blob_text.encode("utf-8")).decode("utf-8")

    def fake_get_json(url: str, *, token: str | None):
        assert token == "ghp_test_token"
        if "/git/trees/" in url:
            return {
                "tree": [
                    {"type": "blob", "path": "docs/guide.md", "sha": "sha-md"},
                    {"type": "blob", "path": "docs/ignore.txt", "sha": "sha-txt"},
                    {"type": "tree", "path": "docs/subdir"},
                ]
            }
        if url.endswith("/git/blobs/sha-md"):
            return {"content": encoded_blob, "encoding": "base64"}
        raise AssertionError(f"Unexpected URL called: {url}")

    monkeypatch.setattr("app.chatbot.knowledge.github_loader.loader.get_json", fake_get_json)

    docs = get_resume_documents(
        repo_url="https://github.com/example-org/example-repo",
        token="ghp_test_token",
        branch="main",
        path_prefix="docs",
    )

    assert len(docs) == 1
    doc = docs[0]
    assert doc.id == "github:docs/guide.md"
    assert doc.title == "Guide"
    assert "Private repo setup details" in doc.text
    assert doc.url == "https://github.com/example-org/example-repo/blob/main/docs/guide.md"


def test_github_loader_uses_first_line_heading_as_title(monkeypatch):
    blob_text = "# Brian Kim\n\nRole: Team Leader"
    encoded_blob = base64.b64encode(blob_text.encode("utf-8")).decode("utf-8")

    def fake_get_json(url: str, *, token: str | None):
        if "/git/trees/" in url:
            return {"tree": [{"type": "blob", "path": "team/realactioner.md", "sha": "sha-brian"}]}
        if url.endswith("/git/blobs/sha-brian"):
            return {"content": encoded_blob, "encoding": "base64"}
        raise AssertionError(f"Unexpected URL called: {url}")

    monkeypatch.setattr("app.chatbot.knowledge.github_loader.loader.get_json", fake_get_json)

    docs = get_resume_documents(
        repo_url="https://github.com/example-org/example-repo",
        token="ghp_test_token",
        branch="main",
        path_prefix="team",
    )

    assert len(docs) == 1
    assert docs[0].title == "Brian Kim"


def test_github_loader_returns_empty_when_repo_url_missing(monkeypatch):
    def fail_if_called(_url: str, *, token: str | None):
        raise AssertionError(f"GitHub API should not be called, got token={token!r}")

    monkeypatch.setattr("app.chatbot.knowledge.github_loader.loader.get_json", fail_if_called)

    docs = get_resume_documents(
        repo_url=None,
        token="ghp_unused_token",
    )

    assert docs == []


def test_github_loader_returns_empty_on_api_error(monkeypatch):
    def failing_get_json(_url: str, *, token: str | None):
        raise HTTPError(
            url="https://api.github.com/repos/example-org/example-repo/git/trees/main?recursive=1",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr("app.chatbot.knowledge.github_loader.loader.get_json", failing_get_json)

    docs = get_resume_documents(
        repo_url="https://github.com/example-org/example-repo",
        token=None,
        branch="main",
    )

    assert docs == []

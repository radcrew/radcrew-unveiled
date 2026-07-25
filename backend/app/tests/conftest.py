"""Shared test fixtures.

Keeps the suite hermetic: no test should need network access or real
credentials to run.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def offline_startup(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Stop app startup from reaching the network.

    ``create_lifespan`` does two remote calls before the app is ready:
    ``get_resume_documents`` pulls Markdown from the GitHub API when
    ``GITHUB_REPO_URL`` is configured, and ``index_documents`` posts the whole
    corpus to the embedding provider. Every ``TestClient(app)`` paid for both,
    which made the suite slow and made it fail whenever GitHub or the inference
    account misbehaved, neither of which is what these tests are checking.

    Both are stubbed to states the code already supports: the static site copy
    still loads, and an empty embedding store makes ``semantic_similarities``
    return zeros so retrieval falls back to lexical matching. Tests that
    exercise the loader or the embeddings call into those modules directly and
    are unaffected.
    """
    monkeypatch.setattr("app.core.lifespan.get_resume_documents", lambda **kwargs: [])
    monkeypatch.setattr("app.core.lifespan.index_documents", lambda documents: None)
    yield

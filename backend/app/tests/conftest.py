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


class _OfflineInferenceClient:
    """Stand-in whose every method refuses to reach the network."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    def __getattr__(self, name: str):
        def refuse(*args: object, **kwargs: object):
            raise ConnectionError(f"network disabled in tests (InferenceClient.{name})")

        return refuse


@pytest.fixture(autouse=True)
def no_live_inference(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Make an unmocked inference call fail instantly instead of going out.

    Guardrails are fail-open by design: ``check_groundedness`` and
    ``check_harmful_input`` swallow errors and return their safe default. That
    is right in production and treacherous in tests, because a test that forgets
    to mock the rails still passes, having quietly spent a real API call and
    however long the provider took to answer. One such test was costing sixteen
    seconds on its own.

    Failing the transport keeps the fail-open paths behaving exactly as they do
    in production while making the leak instant and free. Tests that patch these
    seams themselves override this fixture, since their patches apply later.
    """
    for module in (
        "app.chatbot.huggingface.common",
        "app.chatbot.huggingface.structured",
        "app.chatbot.knowledge.embeddings",
    ):
        monkeypatch.setattr(f"{module}.InferenceClient", _OfflineInferenceClient)

    def refuse_urlopen(*args: object, **kwargs: object):
        raise ConnectionError("network disabled in tests (urlopen)")

    # Patched at the transport rather than at our own wrappers, so the wrappers'
    # error handling stays under test and the block also covers the GitHub
    # loader, web search, and form submit. A test that patches urlopen itself
    # replaces this, because its patch is applied later and undone first.
    monkeypatch.setattr("urllib.request.urlopen", refuse_urlopen)
    yield

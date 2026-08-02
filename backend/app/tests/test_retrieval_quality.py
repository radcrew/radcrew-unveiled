"""Golden set: questions a visitor actually asks, and the document that answers them.

Every other retrieval test asserts on stubbed scores, which proves the ranking
plumbing works but says nothing about whether the right document comes back. This
one runs real embeddings over the real corpus.

It exists because of a concrete miss: "how do I get in touch?" retrieved the
portfolio document instead of contact, and nothing failed. It only surfaced as
wrong follow-up chips in the UI. This is also the measurement to run before and
after any change to chunking, the embedding model, or hybrid search.

Needs a working embedding provider, so it skips rather than failing when one is
absent or out of credit. Every case spends an embedding call, so the module is
marked ``quality`` and deselected by default (see ``pytest.ini``):

    python -m pytest -m quality
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from app.chatbot.graph.nodes.rag_answer.retrieval import retrieve_relevant_documents
from app.chatbot.knowledge import embeddings
from app.chatbot.knowledge.embeddings import index_documents
from app.chatbot.knowledge.site_content import get_static_site_documents
from app.core.settings import get_settings

# How far down the ranking still counts as found. The prompt receives the whole
# corpus, but hints and the confidence gate read this list, so a top-3 hit is
# what actually matters downstream.
TOP_N = 3

pytestmark = pytest.mark.quality

GOLDEN_SET = [
    ("what services do you offer?", "services"),
    ("can you build a smart contract?", "services"),
    ("can you add AI to our existing product?", "services"),
    ("how quickly can you start?", "faq"),
    ("do you offer support after launch?", "faq"),
    ("do you do fixed price contracts?", "faq"),
    ("how do I get in touch?", "contact"),
    ("what is your email address?", "contact"),
    ("where can I find your github?", "social-links"),
    ("how many projects have you shipped?", "stats"),
    ("what technologies do you use?", "tech-stack"),
    ("do you work with Rust?", "tech-stack"),
    pytest.param(
        "what have you built before?",
        "portfolio",
        marks=pytest.mark.xfail(
            reason=(
                "known gap: semantic scores are flat here (stats 0.286, faq 0.240, "
                "portfolio outside the top 5) because the portfolio text names "
                "projects without ever saying 'built before'. The word 'built' does "
                "appear in it, so hybrid search should close this; it is the case to "
                "measure against."
            ),
            strict=False,
        ),
    ),
    ("tell me about CryptoPets", "portfolio"),
    ("how does your process work?", "how-we-work"),
    ("what do your clients say about you?", "testimonial"),
]


@pytest.fixture(autouse=True)
def ignore_dotenv() -> Iterator[None]:
    """Override the hermetic default: this module needs the real HF_TOKEN."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def no_live_inference() -> Iterator[None]:
    """Override the network block: this module measures real embeddings."""
    yield


@pytest.fixture(scope="module")
def corpus():
    documents = get_static_site_documents()
    index_documents(documents)
    if not embeddings._document_vectors:
        pytest.skip("no working embedding provider (unset HF_TOKEN, or out of credit)")
    return documents


@pytest.mark.parametrize(("question", "expected_id"), GOLDEN_SET)
def test_expected_document_is_retrieved(corpus, question: str, expected_id: str) -> None:
    retrieved = retrieve_relevant_documents(corpus, question, limit=TOP_N)
    assert expected_id in [document.id for document in retrieved[:TOP_N]], (
        f"{question!r} returned {[d.id for d in retrieved[:TOP_N]]}"
    )

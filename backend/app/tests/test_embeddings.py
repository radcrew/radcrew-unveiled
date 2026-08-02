"""Embedding: batching for indexing, retry on transient failures, no retry on the query path."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from app.chatbot.knowledge import embeddings

_MODULE = "app.chatbot.knowledge.embeddings"


def _http_error(status: int, message: str) -> Exception:
    """An exception shaped like huggingface_hub's, which carries `.response.status_code`."""
    err = RuntimeError(message)
    err.response = MagicMock(status_code=status)  # type: ignore[attr-defined]
    return err


def _client(side_effect) -> MagicMock:
    client = MagicMock()
    client.feature_extraction.side_effect = side_effect
    return client


def _rows(count: int, value: float = 1.0) -> np.ndarray:
    return np.full((count, 3), value, dtype="float32")


def test_embed_batched_splits_at_the_configured_batch_size() -> None:
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL="m", EMBEDDING_BATCH_SIZE=2)
    client = _client([_rows(2), _rows(2), _rows(1)])

    with patch(f"{_MODULE}._get_client", return_value=client), patch(
        f"{_MODULE}.get_settings", return_value=settings
    ):
        out = embeddings.embed_batched([f"t{i}" for i in range(5)])

    assert client.feature_extraction.call_count == 3
    assert out is not None and out.shape == (5, 3)


def test_embed_batched_keeps_input_order_across_batches() -> None:
    # Callers match vectors to chunks by position, so a reordered concatenation
    # would attach every embedding to the wrong text.
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL="m", EMBEDDING_BATCH_SIZE=2)
    # Distinguishable directions: magnitude cannot identify a batch, since
    # normalization maps [1,1,1] and [2,2,2] onto the same unit vector.
    first = np.array([[1.0, 0.0, 0.0]] * 2, dtype="float32")
    second = np.array([[0.0, 1.0, 0.0]] * 2, dtype="float32")
    client = _client([first, second])

    with patch(f"{_MODULE}._get_client", return_value=client), patch(
        f"{_MODULE}.get_settings", return_value=settings
    ):
        out = embeddings.embed_batched(["a", "b", "c", "d"])

    assert out is not None
    assert list(out[0]) == [1.0, 0.0, 0.0]
    assert list(out[2]) == [0.0, 1.0, 0.0]


def test_embed_batched_rows_are_l2_normalized() -> None:
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL="m", EMBEDDING_BATCH_SIZE=64)
    client = _client([np.array([[3.0, 4.0, 0.0]], dtype="float32")])

    with patch(f"{_MODULE}._get_client", return_value=client), patch(
        f"{_MODULE}.get_settings", return_value=settings
    ):
        out = embeddings.embed_batched(["a"])

    assert out is not None
    assert np.linalg.norm(out[0]) == 1.0


@patch(f"{_MODULE}.sleep")
def test_embed_batched_retries_a_transient_failure(mock_sleep: MagicMock) -> None:
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL="m", EMBEDDING_BATCH_SIZE=64)
    client = _client([_http_error(503, "Service Unavailable"), _rows(1)])

    with patch(f"{_MODULE}._get_client", return_value=client), patch(
        f"{_MODULE}.get_settings", return_value=settings
    ):
        out = embeddings.embed_batched(["a"])

    assert out is not None and out.shape == (1, 3)
    assert client.feature_extraction.call_count == 2
    mock_sleep.assert_called_once()


@patch(f"{_MODULE}.sleep")
def test_embed_batched_does_not_retry_a_depleted_account(mock_sleep: MagicMock) -> None:
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL="m", EMBEDDING_BATCH_SIZE=64)
    client = _client([_http_error(402, "depleted credits"), _rows(1)])

    with patch(f"{_MODULE}._get_client", return_value=client), patch(
        f"{_MODULE}.get_settings", return_value=settings
    ):
        assert embeddings.embed_batched(["a"]) is None

    assert client.feature_extraction.call_count == 1
    mock_sleep.assert_not_called()


@patch(f"{_MODULE}.sleep")
def test_embed_batched_returns_nothing_when_a_batch_is_unrecoverable(mock_sleep: MagicMock) -> None:
    """A short array would misalign every vector after the failed batch."""
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL="m", EMBEDDING_BATCH_SIZE=2)
    client = _client([_rows(2), _http_error(402, "depleted credits")])

    with patch(f"{_MODULE}._get_client", return_value=client), patch(
        f"{_MODULE}.get_settings", return_value=settings
    ):
        assert embeddings.embed_batched(["a", "b", "c"]) is None


def test_embed_batched_without_a_client_returns_nothing() -> None:
    with patch(f"{_MODULE}._get_client", return_value=None), patch(
        f"{_MODULE}.get_settings", return_value=MagicMock(EMBEDDING_BATCH_SIZE=64)
    ):
        assert embeddings.embed_batched(["a"]) is None


def test_embed_batched_of_nothing_calls_no_provider() -> None:
    client = _client([])
    with patch(f"{_MODULE}._get_client", return_value=client):
        assert embeddings.embed_batched([]) is None
    client.feature_extraction.assert_not_called()


@patch(f"{_MODULE}.sleep")
def test_the_query_path_is_not_retried(mock_sleep: MagicMock) -> None:
    """A query embed already degrades to lexical matching; a backoff would
    delay every answer to rescue a few."""
    settings = MagicMock(HUGGINGFACE_EMBEDDING_MODEL="m")
    client = _client([_http_error(503, "Service Unavailable"), _rows(1)])

    with patch(f"{_MODULE}._get_client", return_value=client), patch(
        f"{_MODULE}.get_settings", return_value=settings
    ):
        assert embeddings._embed(["a query"]) is None

    assert client.feature_extraction.call_count == 1
    mock_sleep.assert_not_called()

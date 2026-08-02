from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_settings_defaults_without_env_file() -> None:
    s = Settings(_env_file=None)
    assert s.PORT == 8787
    assert s.FRONTEND_ORIGIN == "https://radcrew.org"
    assert s.HF_TOKEN is None


def test_vector_store_is_off_without_a_database_url() -> None:
    """No DATABASE_URL keeps retrieval on the in-process vector cache."""
    assert Settings(_env_file=None).vector_store_enabled() is False


def test_vector_store_is_enabled_by_the_credential_alone() -> None:
    s = Settings(_env_file=None, DATABASE_URL="postgresql://u:p@h/db?sslmode=require")
    assert s.vector_store_enabled() is True


def test_embedding_batch_size_defaults_and_stays_positive() -> None:
    assert Settings(_env_file=None).EMBEDDING_BATCH_SIZE == 64
    with pytest.raises(ValidationError):
        Settings(_env_file=None, EMBEDDING_BATCH_SIZE=0)


def test_cors_allow_origins_defaults_to_single_frontend_origin() -> None:
    s = Settings(_env_file=None)
    assert s.cors_allow_origins() == ["https://radcrew.org"]


def test_cors_allow_origins_splits_and_strips_the_list() -> None:
    s = Settings(_env_file=None, FRONTEND_ORIGINS=" https://a.dev , https://b.dev ")
    assert s.cors_allow_origins() == ["https://a.dev", "https://b.dev"]


def test_cors_allow_origins_never_returns_empty() -> None:
    """A separators-only value must not blank the allowlist and reject everything."""
    for raw in (",", " , , "):
        s = Settings(_env_file=None, FRONTEND_ORIGINS=raw)
        assert s.cors_allow_origins() == ["https://radcrew.org"]

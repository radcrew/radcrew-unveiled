from __future__ import annotations

from app.core.settings import Settings


def test_settings_defaults_without_env_file() -> None:
    s = Settings(_env_file=None)
    assert s.PORT == 8787
    assert s.FRONTEND_ORIGIN == "http://localhost:8080"
    assert s.HUGGINGFACE_API_KEY is None

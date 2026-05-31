"""
=============================================================================
CONFIGURATION TESTS
=============================================================================

Focused tests for backend settings parsing and startup stability.

Tests must NEVER load the real `backend/.env` — doing so leaks production
secrets into pytest output on any failure and makes the test non-hermetic.
Use `_env_file=None` so Pydantic ignores the dotenv file entirely.
"""

import pytest


def _build_settings(**env):
    """Construct a fresh Settings instance with .env disabled."""
    from app.config import Settings

    return Settings(_env_file=None, **env)


def test_settings_normalize_loose_bool_env_values(monkeypatch):
    """Settings should tolerate non-boolean env strings without crashing."""
    monkeypatch.setenv("DEBUG", "release")
    monkeypatch.setenv("REDIS_ENABLED", "yes")
    monkeypatch.setenv("SMTP_USE_TLS", "0")
    monkeypatch.setenv("EMAIL_TRANSPORT", "disabled")
    # Strong SECRET_KEY required when DEBUG=False survives normalization.
    monkeypatch.setenv(
        "SECRET_KEY", "test-strong-secret-key-0123456789abcdef0123456789"
    )
    # Avoid tripping the production env validator on CORS/REDIS/DB rules.
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_USE_REDIS", "false")
    monkeypatch.setenv("TOKEN_BLACKLIST_USE_REDIS", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")

    settings = _build_settings()

    assert settings.DEBUG is False
    assert settings.REDIS_ENABLED is True
    assert settings.SMTP_USE_TLS is False
    assert settings.EMAIL_TRANSPORT == "disabled"

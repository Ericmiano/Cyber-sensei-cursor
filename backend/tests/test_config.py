"""Test configuration and settings."""
import pytest
from app.core.config import Settings


def test_settings_validation():
    """Test that settings are properly validated."""
    # Test with valid SECRET_KEY
    settings = Settings(
        SECRET_KEY="test-secret-key-at-least-32-characters-long",
        DATABASE_URL="postgresql+asyncpg://test:test@localhost/test",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) >= 32


def test_secret_key_required_in_production():
    """Test that SECRET_KEY is required in production."""
    with pytest.raises(ValueError):
        Settings(
            SECRET_KEY="short",  # Too short
            ENVIRONMENT="production",
            DATABASE_URL="postgresql+asyncpg://test:test@localhost/test",
            REDIS_URL="redis://localhost:6379/0",
        )


def test_default_values():
    """Test default configuration values."""
    settings = Settings(
        SECRET_KEY="test-secret-key-at-least-32-characters-long",
        DATABASE_URL="postgresql+asyncpg://test:test@localhost/test",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert settings.APP_NAME == "Cyber Sensei"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert settings.BKT_INITIAL_MASTERY == 0.3
    assert settings.SM2_INITIAL_EASINESS == 2.5


def test_cors_origins():
    """Test CORS origins configuration."""
    settings = Settings(
        SECRET_KEY="test-secret-key-at-least-32-characters-long",
        DATABASE_URL="postgresql+asyncpg://test:test@localhost/test",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert "http://localhost:5173" in settings.CORS_ORIGINS
    assert "http://localhost:3000" in settings.CORS_ORIGINS

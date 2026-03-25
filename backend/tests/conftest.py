"""Pytest configuration and fixtures."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient


# Use app's DATABASE_URL from settings (.env) - models use PostgreSQL-specific types (UUID, ARRAY, JSONB)
# Override with TEST_DATABASE_URL for a dedicated test database
def _get_test_db_url():
    url = os.getenv("TEST_DATABASE_URL")
    if url:
        return url
    from app.core.config import settings
    return settings.DATABASE_URL


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create test database session."""
    db_url = _get_test_db_url()
    engine = create_async_engine(
        db_url,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(test_db):
    """Create test client with database override."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db):
    """Create a test user."""
    from app.models.users import User, UserProfile
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    profile = UserProfile(user_id=user.id)
    test_db.add(profile)
    await test_db.commit()

    return user

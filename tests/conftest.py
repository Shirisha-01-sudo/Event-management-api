"""Test configuration module."""

import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import settings
from app.db.base import Base
from app.main import app
from app.db.database import get_db


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Override settings for testing
settings.DATABASE_URL = TEST_DATABASE_URL


# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.

    Yields:
        AsyncSession: Database session
    """
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client() -> TestClient:
    """
    Create a FastAPI test client.

    Returns:
        TestClient: Test client
    """
    return TestClient(app)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for async tests.

    Returns:
        EventLoop: Event loop
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_db_setup():
    """
    Set up the test database.

    Creates and drops all tables for tests.
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(async_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session for tests.

    Args:
        async_db_setup: Database setup fixture

    Yields:
        AsyncSession: Database session
    """
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def async_client(async_db_setup) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async client for tests.

    Args:
        async_db_setup: Database setup fixture

    Yields:
        AsyncClient: Async test client
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

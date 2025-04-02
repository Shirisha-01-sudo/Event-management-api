"""Database configuration module."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from app.core.config import settings

# Create async engine for the database
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    future=True,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncSession:
    """
    Get a database session for dependency injection.

    Returns:
        AsyncSession: A database session.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

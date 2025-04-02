"""Base module for database models."""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


async def create_database_tables():
    """Create all database tables asynchronously."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.core.config import settings

    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

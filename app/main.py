"""Main application module."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.api import api_router
from app.core.config import settings
from app.db.base import create_database_tables
from app.middleware.register import register_middleware


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    This handles startup and shutdown events.
    """
    # Startup: create database tables
    logger.info("Creating database tables...")
    await create_database_tables()
    logger.info("Database tables created")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Register middleware
register_middleware(app)

# Include API router
app.include_router(api_router)


@app.get("/", tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status
    """
    return {"status": "healthy", "api_version": settings.APP_VERSION}

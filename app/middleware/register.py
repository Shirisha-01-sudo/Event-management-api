"""Middleware registration module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.auth_middleware import AuthMiddleware


def register_middleware(app: FastAPI) -> None:
    """
    Register all middleware with the FastAPI application.

    Args:
        app: FastAPI application
    """
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add authentication middleware (optional based on configuration)
    if settings.ENVIRONMENT != "development":
        app.add_middleware(AuthMiddleware)

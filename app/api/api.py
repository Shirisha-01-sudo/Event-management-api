"""Main API router module."""

from fastapi import APIRouter

from app.api.routers import event_router, attendee_router, user_router

# Create main API router
api_router = APIRouter()

# Include routers
api_router.include_router(event_router.router)
api_router.include_router(attendee_router.router)
api_router.include_router(user_router.router)

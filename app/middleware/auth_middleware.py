"""Authentication middleware module."""

import logging
from typing import Callable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import JWTError
from app.utils.auth import verify_token

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """
    Authentication middleware for JWT tokens.

    This middleware checks for a valid JWT token in the Authorization header
    for protected routes.
    """

    def __init__(
        self,
        app: Callable,
        exclude_paths: list[str] = None,
        public_paths: list[str] = None,
    ):
        """
        Initialize middleware.

        Args:
            app: The ASGI app
            exclude_paths: Paths to exclude from authentication completely (e.g., /docs)
            public_paths: Paths that don't require authentication but get user info if provided
        """
        self.app = app
        self.exclude_paths = exclude_paths or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/users/login",
            "/users",  # Allow user registration
        ]
        self.public_paths = public_paths or [
            "/events",  # Public events listing
        ]

    async def __call__(self, scope, receive, send):
        """
        ASGI middleware call method.

        Args:
            scope: ASGI scope
            receive: ASGI receive function
            send: ASGI send function
        """
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope=scope, receive=receive)
        path = request.url.path

        # Skip authentication for excluded paths
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await self.app(scope, receive, send)

        # Get token from header
        auth_header = request.headers.get("Authorization")

        # Public paths don't require authentication but benefit from it if provided
        if any(path.startswith(public) for public in self.public_paths):
            if not auth_header or not auth_header.startswith("Bearer "):
                # No token for public path, proceed without user info
                return await self.app(scope, receive, send)
        else:
            # Protected path, require valid token
            if not auth_header or not auth_header.startswith("Bearer "):
                return await self.unauthorized_response(receive, send)

        # If we have a token, verify it
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")

            try:
                # Verify token
                payload = verify_token(token)

                # Add user info to request state
                request.state.user = payload

            except JWTError as e:
                logger.warning(f"Invalid token: {e}")
                # Only return unauthorized for protected paths
                if not any(path.startswith(public) for public in self.public_paths):
                    return await self.unauthorized_response(receive, send)

        return await self.app(scope, receive, send)

    async def unauthorized_response(self, receive, send):
        """
        Send unauthorized response.

        Args:
            receive: ASGI receive function
            send: ASGI send function
        """
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid authentication credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )

        await response({"type": "http"}, receive, send)

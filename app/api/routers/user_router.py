"""User router module."""

from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, Token
from app.services import user_service
from app.utils.auth import create_access_token, get_current_user
from app.core.config import settings

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Create a new user.

    Args:
        user_data: User data
        db: Database session from dependency

    Returns:
        UserResponse: Created user
    """
    user = await user_service.create_user(db, user_data)

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login to get access token.

    Args:
        form_data: Login form data
        db: Database session from dependency

    Returns:
        Token: JWT token

    Raises:
        HTTPException: If login fails
    """
    user = await user_service.authenticate_user(
        db, form_data.username, form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "username": user.username},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Get current user.

    Args:
        current_user: Current user data from token
        db: Database session from dependency

    Returns:
        UserResponse: Current user
    """
    user = await user_service.get_user(db, int(current_user["user_id"]))

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update current user.

    Args:
        user_data: User update data
        current_user: Current user data from token
        db: Database session from dependency

    Returns:
        UserResponse: Updated user
    """
    # Ensure user cannot update admin status
    if hasattr(user_data, "is_admin"):
        delattr(user_data, "is_admin")

    user = await user_service.update_user(db, int(current_user["user_id"]), user_data)

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
    )

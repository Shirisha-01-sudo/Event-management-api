"""User schema models."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common attributes."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, description="Password")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    email: Optional[EmailStr] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    password: Optional[str] = Field(None, min_length=8, description="Password")
    is_active: Optional[bool] = Field(None, description="Is user active")
    is_admin: Optional[bool] = Field(None, description="Is user admin")


class UserResponse(UserBase):
    """Schema for user response."""

    user_id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Is user active")
    is_admin: bool = Field(..., description="Is user admin")

    class Config:
        """Pydantic config class."""

        orm_mode = True
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class TokenData(BaseModel):
    """Schema for JWT token data."""

    username: Optional[str] = Field(None, description="Username")


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

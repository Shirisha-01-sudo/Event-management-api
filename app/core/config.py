"""Configuration settings for the application."""

import os
from typing import Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings class."""

    # General settings
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    APP_TITLE: str = "Event Management API"
    APP_DESCRIPTION: str = "API for managing events and attendees"
    APP_VERSION: str = "0.1.0"

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./events.db")

    # JWT Authentication settings
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET", "your_super_secret_key_change_this_in_production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

    class Config:
        """Pydantic config class."""

        case_sensitive = True


settings = Settings()

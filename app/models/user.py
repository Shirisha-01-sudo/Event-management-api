"""User database model module."""

from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base


class User(Base):
    """User database model."""

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        """
        String representation of the User object.

        Returns:
            str: String representation.
        """
        return f"User(id={self.user_id}, username={self.username}, email={self.email})"

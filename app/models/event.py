"""Event database model module."""

from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.base import Base


class EventStatus(str, Enum):
    """Event status enumeration."""

    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELED = "canceled"


class Event(Base):
    """Event database model."""

    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    max_attendees = Column(Integer, nullable=False)
    status = Column(
        SQLAlchemyEnum(EventStatus),
        nullable=False,
        default=EventStatus.SCHEDULED,
    )

    # Relationship to attendees
    attendees = relationship(
        "Attendee", back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        String representation of the Event object.

        Returns:
            str: String representation.
        """
        return f"Event(id={self.event_id}, name={self.name}, status={self.status})"

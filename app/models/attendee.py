"""Attendee database model module."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.event import Base


class Attendee(Base):
    """Attendee database model."""

    __tablename__ = "attendees"

    attendee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone_number = Column(String, nullable=True)
    event_id = Column(
        Integer, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False
    )
    check_in_status = Column(Boolean, default=False, nullable=False)

    # Relationship to event
    event = relationship("Event", back_populates="attendees")

    def __repr__(self) -> str:
        """
        String representation of the Attendee object.

        Returns:
            str: String representation.
        """
        return f"Attendee(id={self.attendee_id}, name={self.first_name} {self.last_name}, event_id={self.event_id})"

"""Event schema models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.models.event import EventStatus


class EventBase(BaseModel):
    """Base event schema with common attributes."""

    name: str = Field(..., min_length=1, max_length=100, description="Event name")
    description: Optional[str] = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    location: str = Field(
        ..., min_length=1, max_length=255, description="Event location"
    )
    max_attendees: int = Field(..., gt=0, description="Maximum number of attendees")

    @validator("end_time")
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate that end_time is after start_time."""
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class EventCreate(EventBase):
    """Schema for creating a new event."""

    status: EventStatus = Field(
        default=EventStatus.SCHEDULED,
        description="Event status",
    )


class EventUpdate(BaseModel):
    """Schema for updating an event."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Event name"
    )
    description: Optional[str] = Field(None, description="Event description")
    start_time: Optional[datetime] = Field(None, description="Event start time")
    end_time: Optional[datetime] = Field(None, description="Event end time")
    location: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Event location"
    )
    max_attendees: Optional[int] = Field(
        None, gt=0, description="Maximum number of attendees"
    )
    status: Optional[EventStatus] = Field(None, description="Event status")

    @validator("end_time")
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate end_time is after start_time if both are provided."""
        if (
            v is not None
            and "start_time" in values
            and values["start_time"] is not None
        ):
            if v <= values["start_time"]:
                raise ValueError("end_time must be after start_time")
        return v


class EventResponse(EventBase):
    """Schema for event response."""

    event_id: int = Field(..., description="Event ID")
    status: EventStatus = Field(..., description="Event status")
    attendee_count: int = Field(0, description="Number of registered attendees")

    class Config:
        """Pydantic config class."""

        orm_mode = True
        from_attributes = True


class EventList(BaseModel):
    """Schema for list of events."""

    events: List[EventResponse] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of events per page")

"""Attendee schema models."""

from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class AttendeeBase(BaseModel):
    """Base attendee schema with common attributes."""

    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")


class AttendeeCreate(AttendeeBase):
    """Schema for creating a new attendee."""

    event_id: int = Field(..., description="Event ID")


class AttendeeUpdate(BaseModel):
    """Schema for updating an attendee."""

    first_name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="First name"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Last name"
    )
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    check_in_status: Optional[bool] = Field(None, description="Check-in status")


class AttendeeResponse(AttendeeBase):
    """Schema for attendee response."""

    attendee_id: int = Field(..., description="Attendee ID")
    event_id: int = Field(..., description="Event ID")
    check_in_status: bool = Field(..., description="Check-in status")

    class Config:
        """Pydantic config class."""

        orm_mode = True
        from_attributes = True


class AttendeeList(BaseModel):
    """Schema for list of attendees."""

    attendees: List[AttendeeResponse] = Field(..., description="List of attendees")
    total: int = Field(..., description="Total number of attendees")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of attendees per page")


class AttendeeCsv(BaseModel):
    """Schema for CSV attendee record."""

    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None


class AttendeeBulkCreate(BaseModel):
    """Schema for bulk creating attendees."""

    event_id: int = Field(..., description="Event ID")
    attendees: List[AttendeeCsv] = Field(..., description="List of attendees to create")

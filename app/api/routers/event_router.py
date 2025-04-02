"""Event router module."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.event import EventStatus
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventList
from app.services import event_service

router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    """
    Create a new event.

    Args:
        event_data: Event data
        db: Database session from dependency

    Returns:
        EventResponse: Created event
    """
    event = await event_service.create_event(db, event_data)

    # Get attendee count
    attendee_count = await event_service.get_attendee_count(db, event.event_id)

    return EventResponse(
        event_id=event.event_id,
        name=event.name,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        max_attendees=event.max_attendees,
        status=event.status,
        attendee_count=attendee_count,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def read_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    """
    Get event by ID.

    Args:
        event_id: Event ID
        db: Database session from dependency

    Returns:
        EventResponse: Event
    """
    event = await event_service.get_event(db, event_id)

    # Get attendee count
    attendee_count = await event_service.get_attendee_count(db, event.event_id)

    return EventResponse(
        event_id=event.event_id,
        name=event.name,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        max_attendees=event.max_attendees,
        status=event.status,
        attendee_count=attendee_count,
    )


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    """
    Update an event.

    Args:
        event_id: Event ID
        event_data: Event update data
        db: Database session from dependency

    Returns:
        EventResponse: Updated event
    """
    event = await event_service.update_event(db, event_id, event_data)

    # Get attendee count
    attendee_count = await event_service.get_attendee_count(db, event.event_id)

    return EventResponse(
        event_id=event.event_id,
        name=event.name,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        max_attendees=event.max_attendees,
        status=event.status,
        attendee_count=attendee_count,
    )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an event.

    Args:
        event_id: Event ID
        db: Database session from dependency
    """
    await event_service.delete_event(db, event_id)


@router.get("/", response_model=EventList)
async def list_events(
    status: Optional[EventStatus] = None,
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db),
) -> EventList:
    """
    List events with optional filters.

    Args:
        status: Filter by event status
        location: Filter by event location
        start_date: Filter by start date
        end_date: Filter by end date
        search: Search in name and description
        page: Page number
        page_size: Page size
        db: Database session from dependency

    Returns:
        EventList: List of events
    """
    skip = (page - 1) * page_size

    # Update event statuses
    await event_service.update_event_statuses(db)

    # Get events
    events, total = await event_service.list_events(
        db,
        skip=skip,
        limit=page_size,
        status=status,
        location=location,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )

    # Convert to response models
    event_responses = []
    for event in events:
        # Get attendee count
        attendee_count = await event_service.get_attendee_count(db, event.event_id)

        event_response = EventResponse(
            event_id=event.event_id,
            name=event.name,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            max_attendees=event.max_attendees,
            status=event.status,
            attendee_count=attendee_count,
        )
        event_responses.append(event_response)

    return EventList(
        events=event_responses,
        total=total,
        page=page,
        page_size=page_size,
    )

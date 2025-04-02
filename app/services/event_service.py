"""Event service module."""

from datetime import datetime
from typing import List, Optional, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from fastapi import HTTPException, status

from app.models.event import Event, EventStatus
from app.schemas.event import EventCreate, EventUpdate


async def create_event(db: AsyncSession, event_data: EventCreate) -> Event:
    """
    Create a new event.

    Args:
        db: Database session
        event_data: Event data

    Returns:
        Event: Created event
    """
    event = Event(
        name=event_data.name,
        description=event_data.description,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        location=event_data.location,
        max_attendees=event_data.max_attendees,
        status=event_data.status,
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)

    return event


async def get_event(db: AsyncSession, event_id: int) -> Event:
    """
    Get event by ID.

    Args:
        db: Database session
        event_id: Event ID

    Returns:
        Event: Found event

    Raises:
        HTTPException: If event not found
    """
    result = await db.execute(select(Event).filter(Event.event_id == event_id))
    event = result.scalars().first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found",
        )

    return event


async def update_event(
    db: AsyncSession, event_id: int, event_data: EventUpdate
) -> Event:
    """
    Update an event.

    Args:
        db: Database session
        event_id: Event ID
        event_data: Event update data

    Returns:
        Event: Updated event

    Raises:
        HTTPException: If event not found
    """
    event = await get_event(db, event_id)

    # Update event attributes
    update_data = event_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)

    return event


async def delete_event(db: AsyncSession, event_id: int) -> None:
    """
    Delete an event.

    Args:
        db: Database session
        event_id: Event ID

    Raises:
        HTTPException: If event not found
    """
    event = await get_event(db, event_id)

    await db.delete(event)
    await db.commit()


async def list_events(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[EventStatus] = None,
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
) -> Tuple[List[Event], int]:
    """
    List events with optional filters.

    Args:
        db: Database session
        skip: Number of events to skip
        limit: Maximum number of events to return
        status: Filter by event status
        location: Filter by event location
        start_date: Filter by start date
        end_date: Filter by end date
        search: Search in name and description

    Returns:
        Tuple[List[Event], int]: List of events and total count
    """
    query = select(Event)
    count_query = select(func.count()).select_from(Event)

    # Apply filters
    filters = []

    if status:
        filters.append(Event.status == status)

    if location:
        filters.append(Event.location.ilike(f"%{location}%"))

    if start_date:
        filters.append(Event.start_time >= start_date)

    if end_date:
        filters.append(Event.end_time <= end_date)

    if search:
        search_filter = or_(
            Event.name.ilike(f"%{search}%"),
            Event.description.ilike(f"%{search}%"),
        )
        filters.append(search_filter)

    if filters:
        filter_condition = and_(*filters)
        query = query.filter(filter_condition)
        count_query = count_query.filter(filter_condition)

    # Execute count query
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Event.start_time)

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    return events, total


async def update_event_statuses(db: AsyncSession) -> Dict[str, int]:
    """
    Update event statuses based on start and end times.

    Args:
        db: Database session

    Returns:
        Dict[str, int]: Count of updated events by status
    """
    now = datetime.now()

    # Find events that should be marked as 'ongoing'
    ongoing_query = select(Event).filter(
        Event.status == EventStatus.SCHEDULED,
        Event.start_time <= now,
        Event.end_time > now,
    )
    ongoing_result = await db.execute(ongoing_query)
    ongoing_events = ongoing_result.scalars().all()

    # Find events that should be marked as 'completed'
    completed_query = select(Event).filter(
        Event.status.in_([EventStatus.SCHEDULED, EventStatus.ONGOING]),
        Event.end_time <= now,
    )
    completed_result = await db.execute(completed_query)
    completed_events = completed_result.scalars().all()

    # Update ongoing events
    for event in ongoing_events:
        event.status = EventStatus.ONGOING

    # Update completed events
    for event in completed_events:
        event.status = EventStatus.COMPLETED

    await db.commit()

    return {
        "ongoing": len(ongoing_events),
        "completed": len(completed_events),
    }


async def get_attendee_count(db: AsyncSession, event_id: int) -> int:
    """
    Get the number of attendees for an event.

    Args:
        db: Database session
        event_id: Event ID

    Returns:
        int: Number of attendees
    """
    from app.models.attendee import Attendee

    query = (
        select(func.count()).select_from(Attendee).filter(Attendee.event_id == event_id)
    )
    result = await db.execute(query)

    return result.scalar_one()

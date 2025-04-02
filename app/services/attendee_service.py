"""Attendee service module."""

import io
import pandas as pd
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from fastapi import HTTPException, status, UploadFile

from app.models.attendee import Attendee
from app.schemas.attendee import (
    AttendeeCreate,
    AttendeeUpdate,
    AttendeeCsv,
    AttendeeBulkCreate,
)
from app.services.event_service import get_event


async def create_attendee(db: AsyncSession, attendee_data: AttendeeCreate) -> Attendee:
    """
    Create a new attendee.

    Args:
        db: Database session
        attendee_data: Attendee data

    Returns:
        Attendee: Created attendee

    Raises:
        HTTPException: If event not found or registration limit reached
    """
    # Check if event exists and has space
    event = await get_event(db, attendee_data.event_id)

    # Count existing attendees
    query = (
        select(func.count())
        .select_from(Attendee)
        .filter(Attendee.event_id == event.event_id)
    )
    result = await db.execute(query)
    attendee_count = result.scalar_one()

    # Check if event has reached max attendees
    if attendee_count >= event.max_attendees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Event has reached maximum capacity of {event.max_attendees} attendees",
        )

    # Check if email is already registered for this event
    email_query = select(Attendee).filter(
        Attendee.email == attendee_data.email,
        Attendee.event_id == event.event_id,
    )
    email_result = await db.execute(email_query)
    existing_attendee = email_result.scalars().first()

    if existing_attendee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {attendee_data.email} is already registered for this event",
        )

    # Create attendee
    attendee = Attendee(
        first_name=attendee_data.first_name,
        last_name=attendee_data.last_name,
        email=attendee_data.email,
        phone_number=attendee_data.phone_number,
        event_id=attendee_data.event_id,
        check_in_status=False,
    )

    db.add(attendee)
    await db.commit()
    await db.refresh(attendee)

    return attendee


async def get_attendee(db: AsyncSession, attendee_id: int) -> Attendee:
    """
    Get attendee by ID.

    Args:
        db: Database session
        attendee_id: Attendee ID

    Returns:
        Attendee: Found attendee

    Raises:
        HTTPException: If attendee not found
    """
    result = await db.execute(
        select(Attendee).filter(Attendee.attendee_id == attendee_id)
    )
    attendee = result.scalars().first()

    if not attendee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendee with ID {attendee_id} not found",
        )

    return attendee


async def update_attendee(
    db: AsyncSession, attendee_id: int, attendee_data: AttendeeUpdate
) -> Attendee:
    """
    Update an attendee.

    Args:
        db: Database session
        attendee_id: Attendee ID
        attendee_data: Attendee update data

    Returns:
        Attendee: Updated attendee

    Raises:
        HTTPException: If attendee not found
    """
    attendee = await get_attendee(db, attendee_id)

    # If email is being updated, check if it's already in use for the same event
    if attendee_data.email and attendee_data.email != attendee.email:
        email_query = select(Attendee).filter(
            Attendee.email == attendee_data.email,
            Attendee.event_id == attendee.event_id,
            Attendee.attendee_id != attendee_id,
        )
        email_result = await db.execute(email_query)
        existing_attendee = email_result.scalars().first()

        if existing_attendee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {attendee_data.email} is already registered for this event",
            )

    # Update attendee attributes
    update_data = attendee_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendee, field, value)

    await db.commit()
    await db.refresh(attendee)

    return attendee


async def delete_attendee(db: AsyncSession, attendee_id: int) -> None:
    """
    Delete an attendee.

    Args:
        db: Database session
        attendee_id: Attendee ID

    Raises:
        HTTPException: If attendee not found
    """
    attendee = await get_attendee(db, attendee_id)

    await db.delete(attendee)
    await db.commit()


async def list_attendees(
    db: AsyncSession,
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    checked_in: Optional[bool] = None,
    search: Optional[str] = None,
) -> Tuple[List[Attendee], int]:
    """
    List attendees for an event with optional filters.

    Args:
        db: Database session
        event_id: Event ID
        skip: Number of attendees to skip
        limit: Maximum number of attendees to return
        checked_in: Filter by check-in status
        search: Search in name and email

    Returns:
        Tuple[List[Attendee], int]: List of attendees and total count
    """
    # Verify event exists
    await get_event(db, event_id)

    query = select(Attendee).filter(Attendee.event_id == event_id)
    count_query = (
        select(func.count()).select_from(Attendee).filter(Attendee.event_id == event_id)
    )

    # Apply filters
    if checked_in is not None:
        query = query.filter(Attendee.check_in_status == checked_in)
        count_query = count_query.filter(Attendee.check_in_status == checked_in)

    if search:
        search_filter = or_(
            Attendee.first_name.ilike(f"%{search}%"),
            Attendee.last_name.ilike(f"%{search}%"),
            Attendee.email.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)
        count_query = count_query.filter(search_filter)

    # Execute count query
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Apply pagination
    query = (
        query.offset(skip)
        .limit(limit)
        .order_by(Attendee.first_name, Attendee.last_name)
    )

    # Execute query
    result = await db.execute(query)
    attendees = result.scalars().all()

    return attendees, total


async def check_in_attendee(db: AsyncSession, attendee_id: int) -> Attendee:
    """
    Check in an attendee.

    Args:
        db: Database session
        attendee_id: Attendee ID

    Returns:
        Attendee: Updated attendee

    Raises:
        HTTPException: If attendee not found
    """
    attendee = await get_attendee(db, attendee_id)

    if attendee.check_in_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attendee with ID {attendee_id} is already checked in",
        )

    attendee.check_in_status = True

    await db.commit()
    await db.refresh(attendee)

    return attendee


async def bulk_check_in(
    db: AsyncSession, event_id: int, attendee_ids: List[int]
) -> Dict[str, Any]:
    """
    Bulk check in attendees.

    Args:
        db: Database session
        event_id: Event ID
        attendee_ids: List of attendee IDs to check in

    Returns:
        Dict[str, Any]: Results of the bulk check-in operation
    """
    # Verify event exists
    await get_event(db, event_id)

    # Find attendees to check in
    query = select(Attendee).filter(
        Attendee.event_id == event_id,
        Attendee.attendee_id.in_(attendee_ids),
    )
    result = await db.execute(query)
    attendees = result.scalars().all()

    found_ids = [attendee.attendee_id for attendee in attendees]
    missing_ids = [id for id in attendee_ids if id not in found_ids]
    already_checked_in = []
    newly_checked_in = []

    # Update check-in status
    for attendee in attendees:
        if attendee.check_in_status:
            already_checked_in.append(attendee.attendee_id)
        else:
            attendee.check_in_status = True
            newly_checked_in.append(attendee.attendee_id)

    await db.commit()

    return {
        "total": len(attendee_ids),
        "found": len(attendees),
        "missing": missing_ids,
        "already_checked_in": already_checked_in,
        "newly_checked_in": newly_checked_in,
    }


async def process_csv_upload(
    db: AsyncSession, event_id: int, file: UploadFile
) -> Dict[str, Any]:
    """
    Process a CSV file upload for bulk attendee creation.

    Args:
        db: Database session
        event_id: Event ID
        file: Uploaded CSV file

    Returns:
        Dict[str, Any]: Results of the bulk creation operation

    Raises:
        HTTPException: If event not found, file format invalid, or other errors
    """
    # Verify event exists and has space
    event = await get_event(db, event_id)

    # Count existing attendees
    query = (
        select(func.count()).select_from(Attendee).filter(Attendee.event_id == event_id)
    )
    result = await db.execute(query)
    current_attendee_count = result.scalar_one()

    # Read CSV file
    content = await file.read()

    try:
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV format: {str(e)}",
        )

    required_columns = ["first_name", "last_name", "email"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing_columns)}",
        )

    # Convert to list of AttendeeCsv objects
    try:
        attendees_data = []
        for _, row in df.iterrows():
            attendee_data = AttendeeCsv(
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                phone_number=row.get("phone_number"),
            )
            attendees_data.append(attendee_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV data: {str(e)}",
        )

    # Check if event has enough space
    if current_attendee_count + len(attendees_data) > event.max_attendees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot register {len(attendees_data)} new attendees. "
                f"Event has {event.max_attendees} maximum attendees and "
                f"already has {current_attendee_count} registered."
            ),
        )

    # Check for duplicate emails in the dataset
    emails = [attendee.email for attendee in attendees_data]
    duplicate_emails = [email for email in set(emails) if emails.count(email) > 1]

    if duplicate_emails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate emails in CSV: {', '.join(duplicate_emails[:5])}",
        )

    # Check for emails already registered for this event
    existing_emails_query = select(Attendee.email).filter(
        Attendee.event_id == event_id,
        Attendee.email.in_(emails),
    )
    existing_emails_result = await db.execute(existing_emails_query)
    existing_emails = [row[0] for row in existing_emails_result.all()]

    if existing_emails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Some emails are already registered for this event: "
                f"{', '.join(existing_emails[:5])}"
            ),
        )

    # Create attendees
    created_attendees = []
    for attendee_data in attendees_data:
        attendee = Attendee(
            first_name=attendee_data.first_name,
            last_name=attendee_data.last_name,
            email=attendee_data.email,
            phone_number=attendee_data.phone_number,
            event_id=event_id,
            check_in_status=False,
        )
        db.add(attendee)
        created_attendees.append(attendee)

    await db.commit()

    # Refresh attendees to get their IDs
    for attendee in created_attendees:
        await db.refresh(attendee)

    return {
        "total_created": len(created_attendees),
        "attendee_ids": [attendee.attendee_id for attendee in created_attendees],
    }


async def bulk_create_attendees(
    db: AsyncSession, bulk_data: AttendeeBulkCreate
) -> Dict[str, Any]:
    """
    Bulk create attendees for an event.

    Args:
        db: Database session
        bulk_data: Bulk creation data

    Returns:
        Dict[str, Any]: Results of the bulk creation operation
    """
    event_id = bulk_data.event_id
    attendees_data = bulk_data.attendees

    # Verify event exists and has space
    event = await get_event(db, event_id)

    # Count existing attendees
    query = (
        select(func.count()).select_from(Attendee).filter(Attendee.event_id == event_id)
    )
    result = await db.execute(query)
    current_attendee_count = result.scalar_one()

    # Check if event has enough space
    if current_attendee_count + len(attendees_data) > event.max_attendees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot register {len(attendees_data)} new attendees. "
                f"Event has {event.max_attendees} maximum attendees and "
                f"already has {current_attendee_count} registered."
            ),
        )

    # Check for duplicate emails in the dataset
    emails = [attendee.email for attendee in attendees_data]
    duplicate_emails = [email for email in set(emails) if emails.count(email) > 1]

    if duplicate_emails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate emails in request: {', '.join(duplicate_emails[:5])}",
        )

    # Check for emails already registered for this event
    existing_emails_query = select(Attendee.email).filter(
        Attendee.event_id == event_id,
        Attendee.email.in_(emails),
    )
    existing_emails_result = await db.execute(existing_emails_query)
    existing_emails = [row[0] for row in existing_emails_result.all()]

    if existing_emails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Some emails are already registered for this event: "
                f"{', '.join(existing_emails[:5])}"
            ),
        )

    # Create attendees
    created_attendees = []
    for attendee_data in attendees_data:
        attendee = Attendee(
            first_name=attendee_data.first_name,
            last_name=attendee_data.last_name,
            email=attendee_data.email,
            phone_number=attendee_data.phone_number,
            event_id=event_id,
            check_in_status=False,
        )
        db.add(attendee)
        created_attendees.append(attendee)

    await db.commit()

    # Refresh attendees to get their IDs
    for attendee in created_attendees:
        await db.refresh(attendee)

    return {
        "total_created": len(created_attendees),
        "attendee_ids": [attendee.attendee_id for attendee in created_attendees],
    }

"""Attendee router module."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.attendee import (
    AttendeeCreate,
    AttendeeUpdate,
    AttendeeResponse,
    AttendeeList,
    AttendeeBulkCreate,
)
from app.services import attendee_service

router = APIRouter(
    prefix="/attendees",
    tags=["attendees"],
)


@router.post("/", response_model=AttendeeResponse, status_code=status.HTTP_201_CREATED)
async def create_attendee(
    attendee_data: AttendeeCreate,
    db: AsyncSession = Depends(get_db),
) -> AttendeeResponse:
    """
    Register a new attendee for an event.

    Args:
        attendee_data: Attendee data
        db: Database session from dependency

    Returns:
        AttendeeResponse: Created attendee
    """
    attendee = await attendee_service.create_attendee(db, attendee_data)

    return AttendeeResponse(
        attendee_id=attendee.attendee_id,
        first_name=attendee.first_name,
        last_name=attendee.last_name,
        email=attendee.email,
        phone_number=attendee.phone_number,
        event_id=attendee.event_id,
        check_in_status=attendee.check_in_status,
    )


@router.get("/{attendee_id}", response_model=AttendeeResponse)
async def read_attendee(
    attendee_id: int,
    db: AsyncSession = Depends(get_db),
) -> AttendeeResponse:
    """
    Get attendee by ID.

    Args:
        attendee_id: Attendee ID
        db: Database session from dependency

    Returns:
        AttendeeResponse: Attendee
    """
    attendee = await attendee_service.get_attendee(db, attendee_id)

    return AttendeeResponse(
        attendee_id=attendee.attendee_id,
        first_name=attendee.first_name,
        last_name=attendee.last_name,
        email=attendee.email,
        phone_number=attendee.phone_number,
        event_id=attendee.event_id,
        check_in_status=attendee.check_in_status,
    )


@router.put("/{attendee_id}", response_model=AttendeeResponse)
async def update_attendee(
    attendee_id: int,
    attendee_data: AttendeeUpdate,
    db: AsyncSession = Depends(get_db),
) -> AttendeeResponse:
    """
    Update an attendee.

    Args:
        attendee_id: Attendee ID
        attendee_data: Attendee update data
        db: Database session from dependency

    Returns:
        AttendeeResponse: Updated attendee
    """
    attendee = await attendee_service.update_attendee(db, attendee_id, attendee_data)

    return AttendeeResponse(
        attendee_id=attendee.attendee_id,
        first_name=attendee.first_name,
        last_name=attendee.last_name,
        email=attendee.email,
        phone_number=attendee.phone_number,
        event_id=attendee.event_id,
        check_in_status=attendee.check_in_status,
    )


@router.delete("/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendee(
    attendee_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an attendee.

    Args:
        attendee_id: Attendee ID
        db: Database session from dependency
    """
    await attendee_service.delete_attendee(db, attendee_id)


@router.get("/event/{event_id}", response_model=AttendeeList)
async def list_attendees(
    event_id: int,
    checked_in: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db),
) -> AttendeeList:
    """
    List attendees for an event with optional filters.

    Args:
        event_id: Event ID
        checked_in: Filter by check-in status
        search: Search in name and email
        page: Page number
        page_size: Page size
        db: Database session from dependency

    Returns:
        AttendeeList: List of attendees
    """
    skip = (page - 1) * page_size

    # Get attendees
    attendees, total = await attendee_service.list_attendees(
        db,
        event_id=event_id,
        skip=skip,
        limit=page_size,
        checked_in=checked_in,
        search=search,
    )

    # Convert to response models
    attendee_responses = []
    for attendee in attendees:
        attendee_response = AttendeeResponse(
            attendee_id=attendee.attendee_id,
            first_name=attendee.first_name,
            last_name=attendee.last_name,
            email=attendee.email,
            phone_number=attendee.phone_number,
            event_id=attendee.event_id,
            check_in_status=attendee.check_in_status,
        )
        attendee_responses.append(attendee_response)

    return AttendeeList(
        attendees=attendee_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{attendee_id}/check-in", response_model=AttendeeResponse)
async def check_in_attendee(
    attendee_id: int,
    db: AsyncSession = Depends(get_db),
) -> AttendeeResponse:
    """
    Check in an attendee.

    Args:
        attendee_id: Attendee ID
        db: Database session from dependency

    Returns:
        AttendeeResponse: Updated attendee
    """
    attendee = await attendee_service.check_in_attendee(db, attendee_id)

    return AttendeeResponse(
        attendee_id=attendee.attendee_id,
        first_name=attendee.first_name,
        last_name=attendee.last_name,
        email=attendee.email,
        phone_number=attendee.phone_number,
        event_id=attendee.event_id,
        check_in_status=attendee.check_in_status,
    )


@router.post("/event/{event_id}/check-in-bulk")
async def bulk_check_in(
    event_id: int,
    attendee_ids: List[int],
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk check in attendees.

    Args:
        event_id: Event ID
        attendee_ids: List of attendee IDs to check in
        db: Database session from dependency

    Returns:
        dict: Results of the bulk check-in operation
    """
    result = await attendee_service.bulk_check_in(db, event_id, attendee_ids)
    return result


@router.post("/event/{event_id}/bulk-create")
async def bulk_create_attendees(
    event_id: int,
    bulk_data: AttendeeBulkCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk create attendees for an event.

    Args:
        event_id: Event ID
        bulk_data: Bulk creation data
        db: Database session from dependency

    Returns:
        dict: Results of the bulk creation operation
    """
    # Ensure event ID in path matches event ID in request body
    if event_id != bulk_data.event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event ID in path does not match event ID in request body",
        )

    result = await attendee_service.bulk_create_attendees(db, bulk_data)
    return result


@router.post("/event/{event_id}/upload-csv")
async def upload_csv(
    event_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a CSV file upload for bulk attendee creation.

    Args:
        event_id: Event ID
        file: Uploaded CSV file
        db: Database session from dependency

    Returns:
        dict: Results of the bulk creation operation
    """
    result = await attendee_service.process_csv_upload(db, event_id, file)
    return result

"""Attendee API tests module."""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient

from app.models.event import EventStatus
from app.services import event_service, attendee_service


@pytest.fixture
async def test_event(db_session):
    """Create a test event for attendee tests."""
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    event = await event_service.create_event(
        db_session,
        event_data={
            "name": "Attendee Test Event",
            "description": "Attendee test event description",
            "start_time": start_time,
            "end_time": end_time,
            "location": "Test Location",
            "max_attendees": 100,
            "status": EventStatus.SCHEDULED,
        },
    )

    return event


@pytest.mark.asyncio
async def test_create_attendee(async_client: AsyncClient, db_session, test_event):
    """Test creating an attendee."""
    # Create attendee data
    attendee_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "123-456-7890",
        "event_id": test_event.event_id,
    }

    # Create attendee
    response = await async_client.post("/attendees/", json=attendee_data)

    # Assert response
    assert response.status_code == 201
    assert response.json()["first_name"] == attendee_data["first_name"]
    assert response.json()["last_name"] == attendee_data["last_name"]
    assert response.json()["email"] == attendee_data["email"]
    assert response.json()["phone_number"] == attendee_data["phone_number"]
    assert response.json()["event_id"] == attendee_data["event_id"]
    assert response.json()["check_in_status"] is False
    assert "attendee_id" in response.json()


@pytest.mark.asyncio
async def test_get_attendee(async_client: AsyncClient, db_session, test_event):
    """Test getting an attendee."""
    # Create attendee
    attendee = await attendee_service.create_attendee(
        db_session,
        attendee_data={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "123-456-7891",
            "event_id": test_event.event_id,
        },
    )

    # Get attendee
    response = await async_client.get(f"/attendees/{attendee.attendee_id}")

    # Assert response
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"
    assert response.json()["last_name"] == "Smith"
    assert response.json()["email"] == "jane.smith@example.com"
    assert response.json()["phone_number"] == "123-456-7891"
    assert response.json()["event_id"] == test_event.event_id
    assert response.json()["check_in_status"] is False
    assert response.json()["attendee_id"] == attendee.attendee_id


@pytest.mark.asyncio
async def test_update_attendee(async_client: AsyncClient, db_session, test_event):
    """Test updating an attendee."""
    # Create attendee
    attendee = await attendee_service.create_attendee(
        db_session,
        attendee_data={
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "phone_number": "123-456-7892",
            "event_id": test_event.event_id,
        },
    )

    # Update attendee
    update_data = {
        "first_name": "Robert",
        "phone_number": "123-456-7893",
    }

    response = await async_client.put(
        f"/attendees/{attendee.attendee_id}", json=update_data
    )

    # Assert response
    assert response.status_code == 200
    assert response.json()["first_name"] == update_data["first_name"]
    assert response.json()["last_name"] == "Johnson"  # Unchanged
    assert response.json()["email"] == "bob.johnson@example.com"  # Unchanged
    assert response.json()["phone_number"] == update_data["phone_number"]
    assert response.json()["event_id"] == test_event.event_id
    assert response.json()["attendee_id"] == attendee.attendee_id


@pytest.mark.asyncio
async def test_delete_attendee(async_client: AsyncClient, db_session, test_event):
    """Test deleting an attendee."""
    # Create attendee
    attendee = await attendee_service.create_attendee(
        db_session,
        attendee_data={
            "first_name": "Alice",
            "last_name": "Williams",
            "email": "alice.williams@example.com",
            "phone_number": "123-456-7894",
            "event_id": test_event.event_id,
        },
    )

    # Delete attendee
    response = await async_client.delete(f"/attendees/{attendee.attendee_id}")

    # Assert response
    assert response.status_code == 204

    # Verify attendee is deleted
    get_response = await async_client.get(f"/attendees/{attendee.attendee_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_attendees(async_client: AsyncClient, db_session, test_event):
    """Test listing attendees for an event."""
    # Create multiple attendees
    for i in range(5):
        await attendee_service.create_attendee(
            db_session,
            attendee_data={
                "first_name": f"Attendee{i}",
                "last_name": f"Lastname{i}",
                "email": f"attendee{i}@example.com",
                "phone_number": f"123-456-789{i}",
                "event_id": test_event.event_id,
            },
        )

    # List attendees
    response = await async_client.get(f"/attendees/event/{test_event.event_id}")

    # Assert response
    assert response.status_code == 200
    assert "attendees" in response.json()
    assert "total" in response.json()
    assert response.json()["total"] >= 5
    assert len(response.json()["attendees"]) > 0

    # Check that all attendees are for the correct event
    for attendee in response.json()["attendees"]:
        assert attendee["event_id"] == test_event.event_id


@pytest.mark.asyncio
async def test_check_in_attendee(async_client: AsyncClient, db_session, test_event):
    """Test checking in an attendee."""
    # Create attendee
    attendee = await attendee_service.create_attendee(
        db_session,
        attendee_data={
            "first_name": "Check",
            "last_name": "In",
            "email": "check.in@example.com",
            "phone_number": "123-456-7895",
            "event_id": test_event.event_id,
        },
    )

    # Check in attendee
    response = await async_client.post(f"/attendees/{attendee.attendee_id}/check-in")

    # Assert response
    assert response.status_code == 200
    assert response.json()["check_in_status"] is True
    assert response.json()["attendee_id"] == attendee.attendee_id

    # Verify attendee is checked in
    get_response = await async_client.get(f"/attendees/{attendee.attendee_id}")
    assert get_response.status_code == 200
    assert get_response.json()["check_in_status"] is True


@pytest.mark.asyncio
async def test_bulk_check_in(async_client: AsyncClient, db_session, test_event):
    """Test bulk checking in attendees."""
    # Create attendees
    attendees = []
    for i in range(3):
        attendee = await attendee_service.create_attendee(
            db_session,
            attendee_data={
                "first_name": f"Bulk{i}",
                "last_name": f"CheckIn{i}",
                "email": f"bulk{i}@example.com",
                "phone_number": f"123-456-78{i}",
                "event_id": test_event.event_id,
            },
        )
        attendees.append(attendee)

    # Bulk check in attendees
    attendee_ids = [attendee.attendee_id for attendee in attendees]
    response = await async_client.post(
        f"/attendees/event/{test_event.event_id}/check-in-bulk",
        json=attendee_ids,
    )

    # Assert response
    assert response.status_code == 200
    assert response.json()["total"] == len(attendees)
    assert response.json()["found"] == len(attendees)
    assert len(response.json()["newly_checked_in"]) == len(attendees)

    # Verify attendees are checked in
    for attendee_id in attendee_ids:
        get_response = await async_client.get(f"/attendees/{attendee_id}")
        assert get_response.status_code == 200
        assert get_response.json()["check_in_status"] is True


@pytest.mark.asyncio
async def test_bulk_create_attendees(async_client: AsyncClient, db_session, test_event):
    """Test bulk creating attendees."""
    # Create bulk data
    bulk_data = {
        "event_id": test_event.event_id,
        "attendees": [
            {
                "first_name": "Bulk1",
                "last_name": "Create1",
                "email": "bulk.create1@example.com",
                "phone_number": "123-111-1111",
            },
            {
                "first_name": "Bulk2",
                "last_name": "Create2",
                "email": "bulk.create2@example.com",
                "phone_number": "123-222-2222",
            },
            {
                "first_name": "Bulk3",
                "last_name": "Create3",
                "email": "bulk.create3@example.com",
                "phone_number": "123-333-3333",
            },
        ],
    }

    # Bulk create attendees
    response = await async_client.post(
        f"/attendees/event/{test_event.event_id}/bulk-create",
        json=bulk_data,
    )

    # Assert response
    assert response.status_code == 200
    assert response.json()["total_created"] == len(bulk_data["attendees"])
    assert len(response.json()["attendee_ids"]) == len(bulk_data["attendees"])

    # Verify attendees are created
    list_response = await async_client.get(
        f"/attendees/event/{test_event.event_id}?search=bulk.create"
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["attendees"]) >= len(bulk_data["attendees"])

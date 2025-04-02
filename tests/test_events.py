"""Event API tests module."""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient

from app.models.event import EventStatus
from app.services import event_service


@pytest.mark.asyncio
async def test_create_event(async_client: AsyncClient, db_session):
    """Test creating an event."""
    # Create event data
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    event_data = {
        "name": "Test Event",
        "description": "Test event description",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "location": "Test Location",
        "max_attendees": 100,
        "status": EventStatus.SCHEDULED,
    }

    # Create event
    response = await async_client.post("/events/", json=event_data)

    # Assert response
    assert response.status_code == 201
    assert response.json()["name"] == event_data["name"]
    assert response.json()["description"] == event_data["description"]
    assert response.json()["location"] == event_data["location"]
    assert response.json()["max_attendees"] == event_data["max_attendees"]
    assert response.json()["status"] == event_data["status"]
    assert "event_id" in response.json()


@pytest.mark.asyncio
async def test_get_event(async_client: AsyncClient, db_session):
    """Test getting an event."""
    # Create event
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    event = await event_service.create_event(
        db_session,
        event_data={
            "name": "Test Event 2",
            "description": "Test event description 2",
            "start_time": start_time,
            "end_time": end_time,
            "location": "Test Location 2",
            "max_attendees": 200,
            "status": EventStatus.SCHEDULED,
        },
    )

    # Get event
    response = await async_client.get(f"/events/{event.event_id}")

    # Assert response
    assert response.status_code == 200
    assert response.json()["name"] == "Test Event 2"
    assert response.json()["description"] == "Test event description 2"
    assert response.json()["location"] == "Test Location 2"
    assert response.json()["max_attendees"] == 200
    assert response.json()["status"] == EventStatus.SCHEDULED
    assert response.json()["event_id"] == event.event_id


@pytest.mark.asyncio
async def test_update_event(async_client: AsyncClient, db_session):
    """Test updating an event."""
    # Create event
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    event = await event_service.create_event(
        db_session,
        event_data={
            "name": "Test Event 3",
            "description": "Test event description 3",
            "start_time": start_time,
            "end_time": end_time,
            "location": "Test Location 3",
            "max_attendees": 300,
            "status": EventStatus.SCHEDULED,
        },
    )

    # Update event
    update_data = {
        "name": "Updated Event",
        "description": "Updated description",
        "location": "Updated Location",
    }

    response = await async_client.put(f"/events/{event.event_id}", json=update_data)

    # Assert response
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["description"] == update_data["description"]
    assert response.json()["location"] == update_data["location"]
    assert response.json()["max_attendees"] == 300  # Unchanged
    assert response.json()["status"] == EventStatus.SCHEDULED  # Unchanged
    assert response.json()["event_id"] == event.event_id


@pytest.mark.asyncio
async def test_delete_event(async_client: AsyncClient, db_session):
    """Test deleting an event."""
    # Create event
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    event = await event_service.create_event(
        db_session,
        event_data={
            "name": "Test Event 4",
            "description": "Test event description 4",
            "start_time": start_time,
            "end_time": end_time,
            "location": "Test Location 4",
            "max_attendees": 400,
            "status": EventStatus.SCHEDULED,
        },
    )

    # Delete event
    response = await async_client.delete(f"/events/{event.event_id}")

    # Assert response
    assert response.status_code == 204

    # Verify event is deleted
    get_response = await async_client.get(f"/events/{event.event_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_events(async_client: AsyncClient, db_session):
    """Test listing events."""
    # Create multiple events
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    for i in range(5):
        await event_service.create_event(
            db_session,
            event_data={
                "name": f"List Test Event {i}",
                "description": f"List test event description {i}",
                "start_time": start_time,
                "end_time": end_time,
                "location": "Test Location",
                "max_attendees": 100,
                "status": EventStatus.SCHEDULED,
            },
        )

    # List events
    response = await async_client.get("/events/")

    # Assert response
    assert response.status_code == 200
    assert "events" in response.json()
    assert "total" in response.json()
    assert response.json()["total"] >= 5
    assert len(response.json()["events"]) > 0


@pytest.mark.asyncio
async def test_list_events_with_filters(async_client: AsyncClient, db_session):
    """Test listing events with filters."""
    # Create events with different statuses
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    await event_service.create_event(
        db_session,
        event_data={
            "name": "Filter Test Event 1",
            "description": "Filter test event description",
            "start_time": start_time,
            "end_time": end_time,
            "location": "New York",
            "max_attendees": 100,
            "status": EventStatus.SCHEDULED,
        },
    )

    await event_service.create_event(
        db_session,
        event_data={
            "name": "Filter Test Event 2",
            "description": "Filter test event description",
            "start_time": start_time,
            "end_time": end_time,
            "location": "Los Angeles",
            "max_attendees": 200,
            "status": EventStatus.ONGOING,
        },
    )

    # List events with status filter
    response = await async_client.get(f"/events/?status={EventStatus.ONGOING}")

    # Assert response
    assert response.status_code == 200
    assert "events" in response.json()
    assert len(response.json()["events"]) > 0
    for event in response.json()["events"]:
        assert event["status"] == EventStatus.ONGOING

    # List events with location filter
    response = await async_client.get("/events/?location=New+York")

    # Assert response
    assert response.status_code == 200
    assert "events" in response.json()
    assert len(response.json()["events"]) > 0
    for event in response.json()["events"]:
        assert "New York" in event["location"]

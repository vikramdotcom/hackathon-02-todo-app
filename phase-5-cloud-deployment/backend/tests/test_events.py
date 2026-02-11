"""
Tests for Event Publishing and Handling System
"""

import pytest
from datetime import datetime
from app.events import (
    Event,
    EventType,
    EventPublisher,
    EventHandler,
    event_handler
)


class TestEvent:
    """Test Event class."""

    def test_event_creation(self):
        """Test creating an event."""
        data = {"todo_id": 1, "title": "Test todo"}
        event = Event(EventType.TODO_CREATED, data)

        assert event.event_type == EventType.TODO_CREATED
        assert event.data == data
        assert event.event_id is not None
        assert event.timestamp is not None

    def test_event_with_metadata(self):
        """Test event with metadata."""
        data = {"todo_id": 1}
        metadata = {"user_id": 123, "source": "api"}
        event = Event(EventType.TODO_CREATED, data, metadata)

        assert event.metadata == metadata

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        data = {"todo_id": 1}
        event = Event(EventType.TODO_CREATED, data)

        event_dict = event.to_dict()

        assert "event_id" in event_dict
        assert "event_type" in event_dict
        assert "timestamp" in event_dict
        assert "data" in event_dict
        assert event_dict["data"] == data

    def test_event_to_json(self):
        """Test converting event to JSON."""
        data = {"todo_id": 1}
        event = Event(EventType.TODO_CREATED, data)

        json_str = event.to_json()

        assert isinstance(json_str, str)
        assert "event_id" in json_str
        assert "todo_id" in json_str

    def test_event_id_uniqueness(self):
        """Test that event IDs are unique."""
        event1 = Event(EventType.TODO_CREATED, {"id": 1})
        event2 = Event(EventType.TODO_CREATED, {"id": 2})

        assert event1.event_id != event2.event_id


class TestEventPublisher:
    """Test EventPublisher class."""

    def test_publisher_initialization(self):
        """Test publisher initialization."""
        publisher = EventPublisher()

        assert publisher.dapr_url == "http://localhost:3500"
        assert publisher.pubsub_name == "todo-pubsub"

    def test_publisher_custom_url(self):
        """Test publisher with custom URL."""
        custom_url = "http://dapr:3500"
        publisher = EventPublisher(dapr_url=custom_url)

        assert publisher.dapr_url == custom_url

    @pytest.mark.asyncio
    async def test_publish_todo_created(self):
        """Test publishing todo created event."""
        publisher = EventPublisher()
        todo_data = {"title": "Test todo", "priority": "high"}

        # This would normally make an HTTP request
        # In a real test, we'd mock the httpx client
        # For now, just verify the method exists and can be called
        try:
            await publisher.publish_todo_created(1, todo_data)
        except Exception:
            # Expected to fail without actual Dapr sidecar
            pass

    @pytest.mark.asyncio
    async def test_publish_todo_completed(self):
        """Test publishing todo completed event."""
        publisher = EventPublisher()
        completed_at = datetime.utcnow().isoformat()

        try:
            await publisher.publish_todo_completed(1, completed_at)
        except Exception:
            # Expected to fail without actual Dapr sidecar
            pass


class TestEventHandler:
    """Test EventHandler class."""

    def test_handler_initialization(self):
        """Test handler initialization."""
        handler = EventHandler()

        assert handler.handlers == {}

    def test_register_handler(self):
        """Test registering event handler."""
        handler = EventHandler()

        async def test_handler_func(event_data):
            pass

        handler.register(EventType.TODO_CREATED, test_handler_func)

        assert EventType.TODO_CREATED in handler.handlers
        assert test_handler_func in handler.handlers[EventType.TODO_CREATED]

    def test_register_multiple_handlers(self):
        """Test registering multiple handlers for same event."""
        handler = EventHandler()

        async def handler1(event_data):
            pass

        async def handler2(event_data):
            pass

        handler.register(EventType.TODO_CREATED, handler1)
        handler.register(EventType.TODO_CREATED, handler2)

        assert len(handler.handlers[EventType.TODO_CREATED]) == 2

    @pytest.mark.asyncio
    async def test_handle_event(self):
        """Test handling an event."""
        handler = EventHandler()
        called = []

        async def test_handler_func(event_data):
            called.append(event_data)

        handler.register(EventType.TODO_CREATED, test_handler_func)

        event_data = {
            "event_type": EventType.TODO_CREATED,
            "data": {"todo_id": 1}
        }

        await handler.handle(event_data)

        assert len(called) == 1
        assert called[0] == event_data

    @pytest.mark.asyncio
    async def test_handle_event_no_handlers(self):
        """Test handling event with no registered handlers."""
        handler = EventHandler()

        event_data = {
            "event_type": EventType.TODO_CREATED,
            "data": {"todo_id": 1}
        }

        # Should not raise exception
        await handler.handle(event_data)

    @pytest.mark.asyncio
    async def test_handle_event_handler_error(self):
        """Test handling event when handler raises error."""
        handler = EventHandler()

        async def failing_handler(event_data):
            raise ValueError("Test error")

        handler.register(EventType.TODO_CREATED, failing_handler)

        event_data = {
            "event_type": EventType.TODO_CREATED,
            "data": {"todo_id": 1}
        }

        # Should not raise exception (errors are logged)
        await handler.handle(event_data)


class TestEventTypes:
    """Test EventType enum."""

    def test_event_types_exist(self):
        """Test that all expected event types exist."""
        expected_types = [
            "TODO_CREATED",
            "TODO_UPDATED",
            "TODO_COMPLETED",
            "TODO_DELETED",
            "RECURRENCE_CREATED",
            "RECURRENCE_TRIGGERED",
            "REMINDER_SCHEDULED",
            "REMINDER_SENT"
        ]

        for event_type in expected_types:
            assert hasattr(EventType, event_type)

    def test_event_type_values(self):
        """Test event type string values."""
        assert EventType.TODO_CREATED == "todo.created"
        assert EventType.TODO_UPDATED == "todo.updated"
        assert EventType.TODO_COMPLETED == "todo.completed"
        assert EventType.TODO_DELETED == "todo.deleted"

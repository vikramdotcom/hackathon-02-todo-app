"""
Event Publishing and Handling

Provides utilities for publishing and consuming events via Dapr/Kafka.
"""

import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for the todo application."""

    TODO_CREATED = "todo.created"
    TODO_UPDATED = "todo.updated"
    TODO_COMPLETED = "todo.completed"
    TODO_DELETED = "todo.deleted"
    RECURRENCE_CREATED = "recurrence.created"
    RECURRENCE_TRIGGERED = "recurrence.triggered"
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_SENT = "reminder.sent"


class Event:
    """Base event class."""

    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize event.

        Args:
            event_type: Type of event
            data: Event payload
            metadata: Optional metadata
        """
        self.event_type = event_type
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.event_id = self._generate_event_id()

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "data": self.data,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class EventPublisher:
    """Publish events to message broker."""

    def __init__(self, dapr_url: str = "http://localhost:3500"):
        """
        Initialize event publisher.

        Args:
            dapr_url: Dapr sidecar URL
        """
        self.dapr_url = dapr_url
        self.pubsub_name = "todo-pubsub"

    async def publish(self, event: Event, topic: str = "todo-events") -> bool:
        """
        Publish event to topic.

        Args:
            event: Event to publish
            topic: Topic name

        Returns:
            Success status
        """
        try:
            import httpx

            url = f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/{topic}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=event.to_dict(),
                    headers={"Content-Type": "application/json"}
                )

            if response.status_code == 200:
                logger.info(
                    f"Published event {event.event_id} to topic {topic}",
                    extra={
                        "event_type": event.event_type,
                        "event_id": event.event_id,
                        "topic": topic
                    }
                )
                return True
            else:
                logger.error(
                    f"Failed to publish event: {response.status_code}",
                    extra={"event_id": event.event_id}
                )
                return False

        except Exception as e:
            logger.error(
                f"Error publishing event: {e}",
                extra={"event_id": event.event_id},
                exc_info=True
            )
            return False

    async def publish_todo_created(self, todo_id: int, todo_data: Dict[str, Any]):
        """Publish todo created event."""
        event = Event(
            event_type=EventType.TODO_CREATED,
            data={"todo_id": todo_id, **todo_data}
        )
        await self.publish(event)

    async def publish_todo_completed(self, todo_id: int, completed_at: str):
        """Publish todo completed event."""
        event = Event(
            event_type=EventType.TODO_COMPLETED,
            data={"todo_id": todo_id, "completed_at": completed_at}
        )
        await self.publish(event)

    async def publish_recurrence_triggered(
        self,
        pattern_id: int,
        next_todo_id: int
    ):
        """Publish recurrence triggered event."""
        event = Event(
            event_type=EventType.RECURRENCE_TRIGGERED,
            data={
                "pattern_id": pattern_id,
                "next_todo_id": next_todo_id
            }
        )
        await self.publish(event)


class EventHandler:
    """Handle incoming events."""

    def __init__(self):
        """Initialize event handler."""
        self.handlers: Dict[EventType, list[Callable]] = {}

    def register(self, event_type: EventType, handler: Callable):
        """
        Register event handler.

        Args:
            event_type: Event type to handle
            handler: Handler function
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type}")

    async def handle(self, event_data: Dict[str, Any]):
        """
        Handle incoming event.

        Args:
            event_data: Event data from Dapr
        """
        try:
            event_type = event_data.get("event_type")

            if not event_type:
                logger.warning("Received event without type")
                return

            handlers = self.handlers.get(event_type, [])

            if not handlers:
                logger.warning(f"No handlers registered for {event_type}")
                return

            for handler in handlers:
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(
                        f"Error in event handler: {e}",
                        extra={"event_type": event_type},
                        exc_info=True
                    )

        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)


# Global event publisher and handler instances
event_publisher = EventPublisher()
event_handler = EventHandler()


# Example event handlers
async def handle_todo_created(event_data: Dict[str, Any]):
    """Handle todo created event."""
    logger.info(f"Todo created: {event_data.get('data', {}).get('todo_id')}")


async def handle_todo_completed(event_data: Dict[str, Any]):
    """Handle todo completed event."""
    logger.info(f"Todo completed: {event_data.get('data', {}).get('todo_id')}")


# Register default handlers
event_handler.register(EventType.TODO_CREATED, handle_todo_created)
event_handler.register(EventType.TODO_COMPLETED, handle_todo_completed)

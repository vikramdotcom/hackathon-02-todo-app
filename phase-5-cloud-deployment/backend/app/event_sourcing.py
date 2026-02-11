"""
Event Sourcing Implementation

Store state as a sequence of events for complete audit trail.
"""

import logging
from typing import Dict, Any, Optional, List, Type
from datetime import datetime
from dataclasses import dataclass, field
import json
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Base event class."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    aggregate_id: str = ""
    aggregate_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            aggregate_id=data["aggregate_id"],
            aggregate_type=data["aggregate_type"],
            data=data["data"],
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data.get("version", 1)
        )


class EventStore:
    """Store and retrieve events."""

    def __init__(self):
        """Initialize event store."""
        self.events: List[Event] = []
        self.snapshots: Dict[str, Dict[str, Any]] = {}

    async def append_event(self, event: Event):
        """Append event to store."""
        self.events.append(event)
        logger.info(
            f"Event appended: {event.event_type}",
            extra={"event_id": event.event_id, "aggregate_id": event.aggregate_id}
        )

    async def get_events(
        self,
        aggregate_id: str,
        from_version: int = 0
    ) -> List[Event]:
        """Get events for aggregate."""
        return [
            e for e in self.events
            if e.aggregate_id == aggregate_id and e.version > from_version
        ]

    async def get_all_events(
        self,
        aggregate_type: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Event]:
        """Get all events with optional filters."""
        events = self.events

        if aggregate_type:
            events = [e for e in events if e.aggregate_type == aggregate_type]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events

    async def save_snapshot(
        self,
        aggregate_id: str,
        state: Dict[str, Any],
        version: int
    ):
        """Save aggregate snapshot."""
        self.snapshots[aggregate_id] = {
            "state": state,
            "version": version,
            "timestamp": datetime.utcnow()
        }

        logger.info(f"Snapshot saved: {aggregate_id} at version {version}")

    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Get aggregate snapshot."""
        return self.snapshots.get(aggregate_id)


class Aggregate(ABC):
    """Base aggregate class."""

    def __init__(self, aggregate_id: str):
        """Initialize aggregate."""
        self.aggregate_id = aggregate_id
        self.version = 0
        self.uncommitted_events: List[Event] = []

    @abstractmethod
    def apply_event(self, event: Event):
        """Apply event to aggregate state."""
        pass

    def raise_event(self, event_type: str, data: Dict[str, Any]):
        """Raise new event."""
        self.version += 1

        event = Event(
            event_type=event_type,
            aggregate_id=self.aggregate_id,
            aggregate_type=self.__class__.__name__,
            data=data,
            version=self.version
        )

        self.uncommitted_events.append(event)
        self.apply_event(event)

    def load_from_history(self, events: List[Event]):
        """Load aggregate from event history."""
        for event in events:
            self.apply_event(event)
            self.version = event.version

    def get_uncommitted_events(self) -> List[Event]:
        """Get uncommitted events."""
        return self.uncommitted_events

    def mark_events_committed(self):
        """Mark events as committed."""
        self.uncommitted_events.clear()


class TodoAggregate(Aggregate):
    """Todo aggregate with event sourcing."""

    def __init__(self, aggregate_id: str):
        """Initialize todo aggregate."""
        super().__init__(aggregate_id)
        self.title = ""
        self.description = ""
        self.completed = False
        self.created_at: Optional[datetime] = None

    def create_todo(self, title: str, description: str):
        """Create todo."""
        self.raise_event("TodoCreated", {
            "title": title,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        })

    def update_todo(self, title: Optional[str] = None, description: Optional[str] = None):
        """Update todo."""
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description

        self.raise_event("TodoUpdated", data)

    def complete_todo(self):
        """Complete todo."""
        self.raise_event("TodoCompleted", {
            "completed_at": datetime.utcnow().isoformat()
        })

    def delete_todo(self):
        """Delete todo."""
        self.raise_event("TodoDeleted", {
            "deleted_at": datetime.utcnow().isoformat()
        })

    def apply_event(self, event: Event):
        """Apply event to aggregate."""
        if event.event_type == "TodoCreated":
            self.title = event.data["title"]
            self.description = event.data["description"]
            self.created_at = datetime.fromisoformat(event.data["created_at"])
        elif event.event_type == "TodoUpdated":
            if "title" in event.data:
                self.title = event.data["title"]
            if "description" in event.data:
                self.description = event.data["description"]
        elif event.event_type == "TodoCompleted":
            self.completed = True
        elif event.event_type == "TodoDeleted":
            pass  # Mark as deleted in metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "aggregate_id": self.aggregate_id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "version": self.version
        }


class EventRepository:
    """Repository for aggregates using event sourcing."""

    def __init__(self, event_store: EventStore):
        """Initialize event repository."""
        self.event_store = event_store

    async def save(self, aggregate: Aggregate):
        """Save aggregate."""
        events = aggregate.get_uncommitted_events()

        for event in events:
            await self.event_store.append_event(event)

        aggregate.mark_events_committed()

        # Save snapshot every 10 events
        if aggregate.version % 10 == 0:
            await self.event_store.save_snapshot(
                aggregate.aggregate_id,
                aggregate.to_dict() if hasattr(aggregate, 'to_dict') else {},
                aggregate.version
            )

    async def get(
        self,
        aggregate_id: str,
        aggregate_class: Type[Aggregate]
    ) -> Optional[Aggregate]:
        """Get aggregate by ID."""
        # Try to load from snapshot
        snapshot = await self.event_store.get_snapshot(aggregate_id)

        if snapshot:
            aggregate = aggregate_class(aggregate_id)
            # Load snapshot state
            aggregate.version = snapshot["version"]

            # Load events after snapshot
            events = await self.event_store.get_events(
                aggregate_id,
                from_version=snapshot["version"]
            )
        else:
            # Load all events
            events = await self.event_store.get_events(aggregate_id)

            if not events:
                return None

            aggregate = aggregate_class(aggregate_id)

        aggregate.load_from_history(events)
        return aggregate


class EventProjection(ABC):
    """Base class for event projections."""

    @abstractmethod
    async def handle_event(self, event: Event):
        """Handle event."""
        pass


class TodoListProjection(EventProjection):
    """Projection for todo list view."""

    def __init__(self):
        """Initialize projection."""
        self.todos: Dict[str, Dict[str, Any]] = {}

    async def handle_event(self, event: Event):
        """Handle event."""
        if event.event_type == "TodoCreated":
            self.todos[event.aggregate_id] = {
                "id": event.aggregate_id,
                "title": event.data["title"],
                "description": event.data["description"],
                "completed": False,
                "created_at": event.data["created_at"]
            }
        elif event.event_type == "TodoUpdated":
            if event.aggregate_id in self.todos:
                if "title" in event.data:
                    self.todos[event.aggregate_id]["title"] = event.data["title"]
                if "description" in event.data:
                    self.todos[event.aggregate_id]["description"] = event.data["description"]
        elif event.event_type == "TodoCompleted":
            if event.aggregate_id in self.todos:
                self.todos[event.aggregate_id]["completed"] = True
        elif event.event_type == "TodoDeleted":
            if event.aggregate_id in self.todos:
                del self.todos[event.aggregate_id]

    def get_all_todos(self) -> List[Dict[str, Any]]:
        """Get all todos."""
        return list(self.todos.values())

    def get_active_todos(self) -> List[Dict[str, Any]]:
        """Get active todos."""
        return [t for t in self.todos.values() if not t["completed"]]


class EventBus:
    """Event bus for publishing events."""

    def __init__(self):
        """Initialize event bus."""
        self.subscribers: Dict[str, List[EventProjection]] = {}

    def subscribe(self, event_type: str, projection: EventProjection):
        """Subscribe projection to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(projection)

    async def publish(self, event: Event):
        """Publish event to subscribers."""
        if event.event_type in self.subscribers:
            for projection in self.subscribers[event.event_type]:
                await projection.handle_event(event)

        # Also notify wildcard subscribers
        if "*" in self.subscribers:
            for projection in self.subscribers["*"]:
                await projection.handle_event(event)


class EventReplay:
    """Replay events to rebuild projections."""

    def __init__(self, event_store: EventStore, event_bus: EventBus):
        """Initialize event replay."""
        self.event_store = event_store
        self.event_bus = event_bus

    async def replay_all(self):
        """Replay all events."""
        events = await self.event_store.get_all_events()

        logger.info(f"Replaying {len(events)} events")

        for event in events:
            await self.event_bus.publish(event)

        logger.info("Event replay completed")


# Global instances
event_store = EventStore()
event_repository = EventRepository(event_store)
event_bus = EventBus()
event_replay = EventReplay(event_store, event_bus)

# Projections
todo_list_projection = TodoListProjection()
event_bus.subscribe("TodoCreated", todo_list_projection)
event_bus.subscribe("TodoUpdated", todo_list_projection)
event_bus.subscribe("TodoCompleted", todo_list_projection)
event_bus.subscribe("TodoDeleted", todo_list_projection)


# Helper functions
async def create_todo(title: str, description: str) -> str:
    """Create todo using event sourcing."""
    todo_id = str(uuid.uuid4())
    todo = TodoAggregate(todo_id)
    todo.create_todo(title, description)

    await event_repository.save(todo)

    # Publish events
    for event in todo.get_uncommitted_events():
        await event_bus.publish(event)

    return todo_id


async def get_todo(todo_id: str) -> Optional[TodoAggregate]:
    """Get todo by ID."""
    return await event_repository.get(todo_id, TodoAggregate)


async def get_all_todos() -> List[Dict[str, Any]]:
    """Get all todos from projection."""
    return todo_list_projection.get_all_todos()

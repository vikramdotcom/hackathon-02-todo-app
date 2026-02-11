"""
Message Queue Integration

Integrate with message queues for asynchronous processing.
"""

import logging
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Message:
    """Message entity."""

    def __init__(
        self,
        topic: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        message_id: Optional[str] = None
    ):
        """Initialize message."""
        import uuid
        self.message_id = message_id or str(uuid.uuid4())
        self.topic = topic
        self.payload = payload
        self.priority = priority
        self.timestamp = datetime.utcnow()
        self.headers: Dict[str, str] = {}
        self.retry_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "topic": self.topic,
            "payload": self.payload,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "headers": self.headers,
            "retry_count": self.retry_count
        }

    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


class MessageProducer:
    """Message producer for publishing messages."""

    def __init__(self, broker_url: str):
        """Initialize message producer."""
        self.broker_url = broker_url
        self.connected = False

    async def connect(self):
        """Connect to message broker."""
        # In production, connect to actual broker (RabbitMQ, Kafka, etc.)
        self.connected = True
        logger.info(f"Connected to message broker: {self.broker_url}")

    async def disconnect(self):
        """Disconnect from message broker."""
        self.connected = False
        logger.info("Disconnected from message broker")

    async def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """Publish message to topic."""
        if not self.connected:
            await self.connect()

        message = Message(topic, payload, priority)

        # In production, publish to actual broker
        logger.info(
            f"Published message to {topic}",
            extra={
                "topic": topic,
                "message_id": message.message_id,
                "priority": priority.value
            }
        )

        return message.message_id

    async def publish_batch(
        self,
        topic: str,
        payloads: List[Dict[str, Any]]
    ) -> List[str]:
        """Publish batch of messages."""
        message_ids = []

        for payload in payloads:
            message_id = await self.publish(topic, payload)
            message_ids.append(message_id)

        return message_ids


class MessageConsumer:
    """Message consumer for consuming messages."""

    def __init__(self, broker_url: str, consumer_group: str):
        """Initialize message consumer."""
        self.broker_url = broker_url
        self.consumer_group = consumer_group
        self.connected = False
        self.handlers: Dict[str, List[Callable]] = {}
        self.running = False

    async def connect(self):
        """Connect to message broker."""
        # In production, connect to actual broker
        self.connected = True
        logger.info(f"Consumer connected: {self.consumer_group}")

    async def disconnect(self):
        """Disconnect from message broker."""
        self.connected = False
        logger.info(f"Consumer disconnected: {self.consumer_group}")

    def subscribe(self, topic: str, handler: Callable):
        """Subscribe to topic with handler."""
        if topic not in self.handlers:
            self.handlers[topic] = []

        self.handlers[topic].append(handler)

        logger.info(
            f"Subscribed to topic: {topic}",
            extra={"topic": topic, "consumer_group": self.consumer_group}
        )

    async def start(self):
        """Start consuming messages."""
        if not self.connected:
            await self.connect()

        self.running = True
        logger.info("Started message consumer")

        while self.running:
            # In production, poll messages from broker
            await asyncio.sleep(1)

    def stop(self):
        """Stop consuming messages."""
        self.running = False
        logger.info("Stopped message consumer")

    async def process_message(self, message: Message):
        """Process received message."""
        topic = message.topic

        if topic not in self.handlers:
            logger.warning(f"No handler for topic: {topic}")
            return

        for handler in self.handlers[topic]:
            try:
                await handler(message)
            except Exception as e:
                logger.error(
                    f"Error processing message: {e}",
                    extra={"message_id": message.message_id, "topic": topic},
                    exc_info=True
                )


class DeadLetterQueue:
    """Dead letter queue for failed messages."""

    def __init__(self):
        """Initialize dead letter queue."""
        self.messages: List[Message] = []

    def add_message(self, message: Message, error: str):
        """Add message to DLQ."""
        message.headers["dlq_error"] = error
        message.headers["dlq_timestamp"] = datetime.utcnow().isoformat()
        self.messages.append(message)

        logger.warning(
            f"Message sent to DLQ: {message.message_id}",
            extra={"message_id": message.message_id, "error": error}
        )

    def get_messages(self, limit: int = 100) -> List[Message]:
        """Get messages from DLQ."""
        return self.messages[:limit]

    def retry_message(self, message_id: str) -> Optional[Message]:
        """Retry message from DLQ."""
        for i, message in enumerate(self.messages):
            if message.message_id == message_id:
                message.retry_count += 1
                return self.messages.pop(i)

        return None


class MessageRouter:
    """Route messages to appropriate handlers."""

    def __init__(self):
        """Initialize message router."""
        self.routes: Dict[str, str] = {}

    def add_route(self, pattern: str, target_topic: str):
        """Add routing rule."""
        self.routes[pattern] = target_topic

    def route_message(self, message: Message) -> str:
        """Route message to target topic."""
        # Simple pattern matching
        for pattern, target in self.routes.items():
            if pattern in message.topic:
                return target

        return message.topic


class MessageFilter:
    """Filter messages based on criteria."""

    def __init__(self):
        """Initialize message filter."""
        self.filters: List[Callable] = []

    def add_filter(self, filter_func: Callable):
        """Add filter function."""
        self.filters.append(filter_func)

    def should_process(self, message: Message) -> bool:
        """Check if message should be processed."""
        for filter_func in self.filters:
            if not filter_func(message):
                return False

        return True


class MessageTransformer:
    """Transform messages."""

    def __init__(self):
        """Initialize message transformer."""
        self.transformers: Dict[str, Callable] = {}

    def register_transformer(self, topic: str, transformer: Callable):
        """Register transformer for topic."""
        self.transformers[topic] = transformer

    async def transform(self, message: Message) -> Message:
        """Transform message."""
        if message.topic in self.transformers:
            transformer = self.transformers[message.topic]
            message.payload = await transformer(message.payload)

        return message


class MessageBroker:
    """Message broker abstraction."""

    def __init__(self, broker_url: str):
        """Initialize message broker."""
        self.broker_url = broker_url
        self.producer = MessageProducer(broker_url)
        self.consumers: List[MessageConsumer] = []
        self.dlq = DeadLetterQueue()
        self.router = MessageRouter()
        self.filter = MessageFilter()
        self.transformer = MessageTransformer()

    async def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """Publish message."""
        return await self.producer.publish(topic, payload, priority)

    def create_consumer(self, consumer_group: str) -> MessageConsumer:
        """Create message consumer."""
        consumer = MessageConsumer(self.broker_url, consumer_group)
        self.consumers.append(consumer)
        return consumer

    async def start_consumers(self):
        """Start all consumers."""
        tasks = [consumer.start() for consumer in self.consumers]
        await asyncio.gather(*tasks)

    def stop_consumers(self):
        """Stop all consumers."""
        for consumer in self.consumers:
            consumer.stop()


class EventBus:
    """Event bus for pub/sub messaging."""

    def __init__(self):
        """Initialize event bus."""
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)

    async def publish(self, event_type: str, data: Dict[str, Any]):
        """Publish event."""
        if event_type not in self.subscribers:
            return

        tasks = [
            handler(data)
            for handler in self.subscribers[event_type]
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(
            f"Published event: {event_type}",
            extra={"event_type": event_type, "subscribers": len(tasks)}
        )


class MessageMetrics:
    """Track message queue metrics."""

    def __init__(self):
        """Initialize message metrics."""
        self.published_count = 0
        self.consumed_count = 0
        self.failed_count = 0
        self.processing_times: List[float] = []

    def record_publish(self):
        """Record message published."""
        self.published_count += 1

    def record_consume(self, processing_time_ms: float):
        """Record message consumed."""
        self.consumed_count += 1
        self.processing_times.append(processing_time_ms)

    def record_failure(self):
        """Record message failure."""
        self.failed_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get metrics statistics."""
        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )

        return {
            "published": self.published_count,
            "consumed": self.consumed_count,
            "failed": self.failed_count,
            "avg_processing_time_ms": avg_processing_time,
            "success_rate": (
                self.consumed_count / (self.consumed_count + self.failed_count)
                if (self.consumed_count + self.failed_count) > 0 else 0
            )
        }


class MessageScheduler:
    """Schedule delayed message delivery."""

    def __init__(self, producer: MessageProducer):
        """Initialize message scheduler."""
        self.producer = producer
        self.scheduled_messages: List[Dict[str, Any]] = []

    async def schedule_message(
        self,
        topic: str,
        payload: Dict[str, Any],
        delay_seconds: int
    ):
        """Schedule message for delayed delivery."""
        scheduled_time = datetime.utcnow().timestamp() + delay_seconds

        scheduled = {
            "topic": topic,
            "payload": payload,
            "scheduled_time": scheduled_time
        }

        self.scheduled_messages.append(scheduled)

        logger.info(
            f"Scheduled message for {topic}",
            extra={"topic": topic, "delay_seconds": delay_seconds}
        )

    async def process_scheduled_messages(self):
        """Process scheduled messages."""
        now = datetime.utcnow().timestamp()
        to_send = []

        for scheduled in self.scheduled_messages:
            if scheduled["scheduled_time"] <= now:
                to_send.append(scheduled)

        for scheduled in to_send:
            await self.producer.publish(
                scheduled["topic"],
                scheduled["payload"]
            )
            self.scheduled_messages.remove(scheduled)


# Global instances
message_broker = MessageBroker("localhost:9092")
event_bus = EventBus()
message_metrics = MessageMetrics()


# Helper functions
async def publish_message(
    topic: str,
    payload: Dict[str, Any],
    priority: MessagePriority = MessagePriority.NORMAL
) -> str:
    """Publish message to topic."""
    message_id = await message_broker.publish(topic, payload, priority)
    message_metrics.record_publish()
    return message_id


def subscribe_to_topic(topic: str, handler: Callable):
    """Subscribe to topic."""
    consumer = message_broker.create_consumer("default")
    consumer.subscribe(topic, handler)


async def publish_event(event_type: str, data: Dict[str, Any]):
    """Publish event to event bus."""
    await event_bus.publish(event_type, data)


def subscribe_to_event(event_type: str, handler: Callable):
    """Subscribe to event."""
    event_bus.subscribe(event_type, handler)


# Example handlers
async def handle_todo_created(message: Message):
    """Handle todo created event."""
    logger.info(f"Todo created: {message.payload}")


async def handle_todo_completed(message: Message):
    """Handle todo completed event."""
    logger.info(f"Todo completed: {message.payload}")

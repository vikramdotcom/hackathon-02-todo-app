"""
Webhook Management System

Provides webhook registration, delivery, and retry logic for event notifications.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """Webhook event types."""

    TODO_CREATED = "todo.created"
    TODO_UPDATED = "todo.updated"
    TODO_COMPLETED = "todo.completed"
    TODO_DELETED = "todo.deleted"
    RECURRENCE_TRIGGERED = "recurrence.triggered"
    REMINDER_DUE = "reminder.due"


class WebhookStatus(str, Enum):
    """Webhook delivery status."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook:
    """Webhook subscription."""

    def __init__(
        self,
        id: int,
        url: str,
        events: List[WebhookEvent],
        secret: str,
        active: bool = True,
        description: str = "",
        headers: Optional[Dict[str, str]] = None,
        retry_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize webhook.

        Args:
            id: Webhook ID
            url: Target URL
            events: List of events to subscribe to
            secret: Secret for signature verification
            active: Whether webhook is active
            description: Webhook description
            headers: Custom headers to include
            retry_config: Retry configuration
        """
        self.id = id
        self.url = url
        self.events = events
        self.secret = secret
        self.active = active
        self.description = description
        self.headers = headers or {}
        self.retry_config = retry_config or {
            "max_attempts": 3,
            "initial_delay": 60,
            "backoff_factor": 2
        }
        self.created_at = datetime.utcnow()
        self.last_triggered_at: Optional[datetime] = None
        self.delivery_count = 0
        self.failure_count = 0

    def should_trigger(self, event: WebhookEvent) -> bool:
        """
        Check if webhook should trigger for event.

        Args:
            event: Event type

        Returns:
            True if webhook should trigger
        """
        return self.active and event in self.events

    def generate_signature(self, payload: str) -> str:
        """
        Generate HMAC signature for payload.

        Args:
            payload: JSON payload

        Returns:
            Hex signature
        """
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()


class WebhookDelivery:
    """Webhook delivery attempt."""

    def __init__(
        self,
        webhook_id: int,
        event: WebhookEvent,
        payload: Dict[str, Any],
        attempt: int = 1
    ):
        """
        Initialize delivery.

        Args:
            webhook_id: Webhook ID
            event: Event type
            payload: Event payload
            attempt: Attempt number
        """
        self.webhook_id = webhook_id
        self.event = event
        self.payload = payload
        self.attempt = attempt
        self.status = WebhookStatus.PENDING
        self.created_at = datetime.utcnow()
        self.delivered_at: Optional[datetime] = None
        self.response_status: Optional[int] = None
        self.response_body: Optional[str] = None
        self.error: Optional[str] = None
        self.next_retry_at: Optional[datetime] = None


class WebhookManager:
    """Manage webhooks and deliveries."""

    def __init__(self):
        """Initialize webhook manager."""
        self.webhooks: Dict[int, Webhook] = {}
        self.deliveries: List[WebhookDelivery] = []
        self.next_webhook_id = 1

    def register(
        self,
        url: str,
        events: List[WebhookEvent],
        secret: str,
        **kwargs
    ) -> Webhook:
        """
        Register a new webhook.

        Args:
            url: Target URL
            events: Events to subscribe to
            secret: Secret for signatures
            **kwargs: Additional webhook options

        Returns:
            Created webhook
        """
        webhook = Webhook(
            id=self.next_webhook_id,
            url=url,
            events=events,
            secret=secret,
            **kwargs
        )

        self.webhooks[webhook.id] = webhook
        self.next_webhook_id += 1

        logger.info(
            f"Registered webhook {webhook.id}",
            extra={
                "webhook_id": webhook.id,
                "url": url,
                "events": [e.value for e in events]
            }
        )

        return webhook

    def unregister(self, webhook_id: int):
        """
        Unregister a webhook.

        Args:
            webhook_id: Webhook ID
        """
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"Unregistered webhook {webhook_id}")

    def get_webhook(self, webhook_id: int) -> Optional[Webhook]:
        """
        Get webhook by ID.

        Args:
            webhook_id: Webhook ID

        Returns:
            Webhook or None
        """
        return self.webhooks.get(webhook_id)

    def list_webhooks(
        self,
        event: Optional[WebhookEvent] = None,
        active_only: bool = True
    ) -> List[Webhook]:
        """
        List webhooks.

        Args:
            event: Filter by event type
            active_only: Only return active webhooks

        Returns:
            List of webhooks
        """
        webhooks = list(self.webhooks.values())

        if active_only:
            webhooks = [w for w in webhooks if w.active]

        if event:
            webhooks = [w for w in webhooks if event in w.events]

        return webhooks

    def update_webhook(
        self,
        webhook_id: int,
        active: Optional[bool] = None,
        events: Optional[List[WebhookEvent]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Update webhook configuration.

        Args:
            webhook_id: Webhook ID
            active: New active status
            events: New event list
            headers: New headers
        """
        webhook = self.webhooks.get(webhook_id)

        if webhook is None:
            raise ValueError(f"Webhook {webhook_id} not found")

        if active is not None:
            webhook.active = active

        if events is not None:
            webhook.events = events

        if headers is not None:
            webhook.headers = headers

        logger.info(f"Updated webhook {webhook_id}")

    async def trigger(
        self,
        event: WebhookEvent,
        payload: Dict[str, Any]
    ):
        """
        Trigger webhooks for event.

        Args:
            event: Event type
            payload: Event payload
        """
        webhooks = self.list_webhooks(event=event, active_only=True)

        if not webhooks:
            logger.debug(f"No webhooks registered for {event}")
            return

        logger.info(
            f"Triggering {len(webhooks)} webhooks for {event}",
            extra={"event": event, "webhook_count": len(webhooks)}
        )

        # Trigger all webhooks concurrently
        tasks = [
            self._deliver_webhook(webhook, event, payload)
            for webhook in webhooks
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _deliver_webhook(
        self,
        webhook: Webhook,
        event: WebhookEvent,
        payload: Dict[str, Any]
    ):
        """
        Deliver webhook with retry logic.

        Args:
            webhook: Webhook to deliver
            event: Event type
            payload: Event payload
        """
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event=event,
            payload=payload
        )

        self.deliveries.append(delivery)

        max_attempts = webhook.retry_config["max_attempts"]
        initial_delay = webhook.retry_config["initial_delay"]
        backoff_factor = webhook.retry_config["backoff_factor"]

        for attempt in range(1, max_attempts + 1):
            delivery.attempt = attempt

            if attempt > 1:
                delivery.status = WebhookStatus.RETRYING
                delay = initial_delay * (backoff_factor ** (attempt - 2))
                logger.info(
                    f"Retrying webhook {webhook.id} in {delay}s (attempt {attempt}/{max_attempts})"
                )
                await asyncio.sleep(delay)

            success = await self._send_webhook(webhook, delivery)

            if success:
                delivery.status = WebhookStatus.DELIVERED
                delivery.delivered_at = datetime.utcnow()
                webhook.delivery_count += 1
                webhook.last_triggered_at = datetime.utcnow()

                logger.info(
                    f"Webhook {webhook.id} delivered successfully",
                    extra={
                        "webhook_id": webhook.id,
                        "event": event,
                        "attempt": attempt
                    }
                )
                return

        # All attempts failed
        delivery.status = WebhookStatus.FAILED
        webhook.failure_count += 1

        logger.error(
            f"Webhook {webhook.id} failed after {max_attempts} attempts",
            extra={
                "webhook_id": webhook.id,
                "event": event,
                "error": delivery.error
            }
        )

    async def _send_webhook(
        self,
        webhook: Webhook,
        delivery: WebhookDelivery
    ) -> bool:
        """
        Send webhook HTTP request.

        Args:
            webhook: Webhook to send
            delivery: Delivery record

        Returns:
            True if successful
        """
        try:
            import httpx
            import json

            # Prepare payload
            payload_json = json.dumps(delivery.payload)

            # Generate signature
            signature = webhook.generate_signature(payload_json)

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Event": delivery.event.value,
                "X-Webhook-Signature": signature,
                "X-Webhook-Delivery": str(delivery.webhook_id),
                **webhook.headers
            }

            # Send request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers
                )

            delivery.response_status = response.status_code
            delivery.response_body = response.text[:1000]  # Limit size

            # Consider 2xx status codes as success
            if 200 <= response.status_code < 300:
                return True
            else:
                delivery.error = f"HTTP {response.status_code}"
                return False

        except Exception as e:
            delivery.error = str(e)
            logger.error(
                f"Error sending webhook {webhook.id}: {e}",
                exc_info=True
            )
            return False

    def get_deliveries(
        self,
        webhook_id: Optional[int] = None,
        status: Optional[WebhookStatus] = None,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """
        Get webhook deliveries.

        Args:
            webhook_id: Filter by webhook ID
            status: Filter by status
            limit: Maximum deliveries to return

        Returns:
            List of deliveries
        """
        deliveries = self.deliveries

        if webhook_id is not None:
            deliveries = [d for d in deliveries if d.webhook_id == webhook_id]

        if status is not None:
            deliveries = [d for d in deliveries if d.status == status]

        # Sort by created_at descending
        deliveries = sorted(deliveries, key=lambda d: d.created_at, reverse=True)

        return deliveries[:limit]


# Global webhook manager
webhook_manager = WebhookManager()

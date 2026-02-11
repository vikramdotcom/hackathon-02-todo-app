"""
Tests for Webhook Management System
"""

import pytest
import asyncio
from datetime import datetime
from app.webhooks import (
    Webhook,
    WebhookEvent,
    WebhookStatus,
    WebhookDelivery,
    WebhookManager
)


class TestWebhook:
    """Test Webhook class."""

    def test_webhook_initialization(self):
        """Test webhook initialization."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123",
            description="Test webhook"
        )

        assert webhook.id == 1
        assert webhook.url == "https://example.com/webhook"
        assert WebhookEvent.TODO_CREATED in webhook.events
        assert webhook.secret == "secret123"
        assert webhook.active is True
        assert webhook.description == "Test webhook"

    def test_webhook_with_custom_headers(self):
        """Test webhook with custom headers."""
        headers = {"Authorization": "Bearer token123"}

        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123",
            headers=headers
        )

        assert webhook.headers == headers

    def test_webhook_with_retry_config(self):
        """Test webhook with custom retry configuration."""
        retry_config = {
            "max_attempts": 5,
            "initial_delay": 30,
            "backoff_factor": 3
        }

        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123",
            retry_config=retry_config
        )

        assert webhook.retry_config == retry_config

    def test_webhook_default_retry_config(self):
        """Test webhook default retry configuration."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        assert "max_attempts" in webhook.retry_config
        assert "initial_delay" in webhook.retry_config
        assert "backoff_factor" in webhook.retry_config

    def test_should_trigger_active_webhook(self):
        """Test should_trigger for active webhook."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED, WebhookEvent.TODO_UPDATED],
            secret="secret123",
            active=True
        )

        assert webhook.should_trigger(WebhookEvent.TODO_CREATED) is True
        assert webhook.should_trigger(WebhookEvent.TODO_UPDATED) is True
        assert webhook.should_trigger(WebhookEvent.TODO_DELETED) is False

    def test_should_trigger_inactive_webhook(self):
        """Test should_trigger for inactive webhook."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123",
            active=False
        )

        assert webhook.should_trigger(WebhookEvent.TODO_CREATED) is False

    def test_generate_signature(self):
        """Test HMAC signature generation."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        payload = '{"id": 1, "title": "Test"}'
        signature = webhook.generate_signature(payload)

        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA-256 hex digest length

    def test_generate_signature_consistency(self):
        """Test signature generation is consistent."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        payload = '{"id": 1, "title": "Test"}'
        signature1 = webhook.generate_signature(payload)
        signature2 = webhook.generate_signature(payload)

        assert signature1 == signature2

    def test_generate_signature_different_payloads(self):
        """Test different payloads produce different signatures."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        payload1 = '{"id": 1}'
        payload2 = '{"id": 2}'

        signature1 = webhook.generate_signature(payload1)
        signature2 = webhook.generate_signature(payload2)

        assert signature1 != signature2


class TestWebhookDelivery:
    """Test WebhookDelivery class."""

    def test_delivery_initialization(self):
        """Test delivery initialization."""
        payload = {"id": 1, "title": "Test"}

        delivery = WebhookDelivery(
            webhook_id=1,
            event=WebhookEvent.TODO_CREATED,
            payload=payload
        )

        assert delivery.webhook_id == 1
        assert delivery.event == WebhookEvent.TODO_CREATED
        assert delivery.payload == payload
        assert delivery.attempt == 1
        assert delivery.status == WebhookStatus.PENDING
        assert delivery.created_at is not None

    def test_delivery_with_attempt_number(self):
        """Test delivery with specific attempt number."""
        delivery = WebhookDelivery(
            webhook_id=1,
            event=WebhookEvent.TODO_CREATED,
            payload={},
            attempt=3
        )

        assert delivery.attempt == 3


class TestWebhookManager:
    """Test WebhookManager class."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = WebhookManager()

        assert manager.webhooks == {}
        assert manager.deliveries == []
        assert manager.next_webhook_id == 1

    def test_register_webhook(self):
        """Test registering a webhook."""
        manager = WebhookManager()

        webhook = manager.register(
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123",
            description="Test webhook"
        )

        assert webhook.id == 1
        assert webhook.url == "https://example.com/webhook"
        assert webhook in manager.webhooks.values()

    def test_register_multiple_webhooks(self):
        """Test registering multiple webhooks."""
        manager = WebhookManager()

        webhook1 = manager.register(
            url="https://example.com/webhook1",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret1"
        )

        webhook2 = manager.register(
            url="https://example.com/webhook2",
            events=[WebhookEvent.TODO_UPDATED],
            secret="secret2"
        )

        assert webhook1.id == 1
        assert webhook2.id == 2
        assert len(manager.webhooks) == 2

    def test_unregister_webhook(self):
        """Test unregistering a webhook."""
        manager = WebhookManager()

        webhook = manager.register(
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        manager.unregister(webhook.id)

        assert webhook.id not in manager.webhooks

    def test_get_webhook(self):
        """Test getting webhook by ID."""
        manager = WebhookManager()

        webhook = manager.register(
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        retrieved = manager.get_webhook(webhook.id)

        assert retrieved == webhook

    def test_get_webhook_not_found(self):
        """Test getting non-existent webhook."""
        manager = WebhookManager()

        assert manager.get_webhook(999) is None

    def test_list_webhooks_all(self):
        """Test listing all webhooks."""
        manager = WebhookManager()

        manager.register(
            url="https://example.com/webhook1",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret1"
        )

        manager.register(
            url="https://example.com/webhook2",
            events=[WebhookEvent.TODO_UPDATED],
            secret="secret2"
        )

        webhooks = manager.list_webhooks(active_only=False)

        assert len(webhooks) == 2

    def test_list_webhooks_active_only(self):
        """Test listing only active webhooks."""
        manager = WebhookManager()

        manager.register(
            url="https://example.com/webhook1",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret1",
            active=True
        )

        manager.register(
            url="https://example.com/webhook2",
            events=[WebhookEvent.TODO_UPDATED],
            secret="secret2",
            active=False
        )

        webhooks = manager.list_webhooks(active_only=True)

        assert len(webhooks) == 1
        assert webhooks[0].active is True

    def test_list_webhooks_by_event(self):
        """Test listing webhooks by event type."""
        manager = WebhookManager()

        manager.register(
            url="https://example.com/webhook1",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret1"
        )

        manager.register(
            url="https://example.com/webhook2",
            events=[WebhookEvent.TODO_UPDATED],
            secret="secret2"
        )

        manager.register(
            url="https://example.com/webhook3",
            events=[WebhookEvent.TODO_CREATED, WebhookEvent.TODO_UPDATED],
            secret="secret3"
        )

        webhooks = manager.list_webhooks(event=WebhookEvent.TODO_CREATED)

        assert len(webhooks) == 2

    def test_update_webhook_active_status(self):
        """Test updating webhook active status."""
        manager = WebhookManager()

        webhook = manager.register(
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123",
            active=True
        )

        manager.update_webhook(webhook.id, active=False)

        assert manager.webhooks[webhook.id].active is False

    def test_update_webhook_events(self):
        """Test updating webhook events."""
        manager = WebhookManager()

        webhook = manager.register(
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        new_events = [WebhookEvent.TODO_CREATED, WebhookEvent.TODO_UPDATED]
        manager.update_webhook(webhook.id, events=new_events)

        assert manager.webhooks[webhook.id].events == new_events

    def test_update_webhook_headers(self):
        """Test updating webhook headers."""
        manager = WebhookManager()

        webhook = manager.register(
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        new_headers = {"Authorization": "Bearer token123"}
        manager.update_webhook(webhook.id, headers=new_headers)

        assert manager.webhooks[webhook.id].headers == new_headers

    def test_update_webhook_not_found(self):
        """Test updating non-existent webhook."""
        manager = WebhookManager()

        with pytest.raises(ValueError):
            manager.update_webhook(999, active=False)

    @pytest.mark.asyncio
    async def test_trigger_no_webhooks(self):
        """Test triggering with no registered webhooks."""
        manager = WebhookManager()

        # Should not raise exception
        await manager.trigger(
            WebhookEvent.TODO_CREATED,
            {"id": 1, "title": "Test"}
        )

    @pytest.mark.asyncio
    async def test_trigger_creates_deliveries(self):
        """Test triggering creates delivery records."""
        manager = WebhookManager()

        manager.register(
            url="https://example.com/webhook",
            events=[WebhookEvent.TODO_CREATED],
            secret="secret123"
        )

        # Mock the _send_webhook method to avoid actual HTTP calls
        async def mock_send(webhook, delivery):
            return True

        manager._send_webhook = mock_send

        await manager.trigger(
            WebhookEvent.TODO_CREATED,
            {"id": 1, "title": "Test"}
        )

        assert len(manager.deliveries) == 1
        assert manager.deliveries[0].event == WebhookEvent.TODO_CREATED

    def test_get_deliveries_all(self):
        """Test getting all deliveries."""
        manager = WebhookManager()

        delivery1 = WebhookDelivery(1, WebhookEvent.TODO_CREATED, {})
        delivery2 = WebhookDelivery(1, WebhookEvent.TODO_UPDATED, {})

        manager.deliveries.append(delivery1)
        manager.deliveries.append(delivery2)

        deliveries = manager.get_deliveries()

        assert len(deliveries) == 2

    def test_get_deliveries_by_webhook_id(self):
        """Test filtering deliveries by webhook ID."""
        manager = WebhookManager()

        delivery1 = WebhookDelivery(1, WebhookEvent.TODO_CREATED, {})
        delivery2 = WebhookDelivery(2, WebhookEvent.TODO_CREATED, {})
        delivery3 = WebhookDelivery(1, WebhookEvent.TODO_UPDATED, {})

        manager.deliveries.extend([delivery1, delivery2, delivery3])

        deliveries = manager.get_deliveries(webhook_id=1)

        assert len(deliveries) == 2
        assert all(d.webhook_id == 1 for d in deliveries)

    def test_get_deliveries_by_status(self):
        """Test filtering deliveries by status."""
        manager = WebhookManager()

        delivery1 = WebhookDelivery(1, WebhookEvent.TODO_CREATED, {})
        delivery1.status = WebhookStatus.DELIVERED

        delivery2 = WebhookDelivery(1, WebhookEvent.TODO_UPDATED, {})
        delivery2.status = WebhookStatus.FAILED

        delivery3 = WebhookDelivery(1, WebhookEvent.TODO_DELETED, {})
        delivery3.status = WebhookStatus.DELIVERED

        manager.deliveries.extend([delivery1, delivery2, delivery3])

        deliveries = manager.get_deliveries(status=WebhookStatus.DELIVERED)

        assert len(deliveries) == 2
        assert all(d.status == WebhookStatus.DELIVERED for d in deliveries)

    def test_get_deliveries_limit(self):
        """Test limiting number of deliveries returned."""
        manager = WebhookManager()

        for i in range(10):
            delivery = WebhookDelivery(1, WebhookEvent.TODO_CREATED, {})
            manager.deliveries.append(delivery)

        deliveries = manager.get_deliveries(limit=5)

        assert len(deliveries) == 5

    def test_get_deliveries_sorted_by_created_at(self):
        """Test deliveries are sorted by created_at descending."""
        manager = WebhookManager()

        for i in range(3):
            delivery = WebhookDelivery(1, WebhookEvent.TODO_CREATED, {})
            manager.deliveries.append(delivery)

        deliveries = manager.get_deliveries()

        # Most recent first
        for i in range(len(deliveries) - 1):
            assert deliveries[i].created_at >= deliveries[i + 1].created_at


class TestWebhookEvent:
    """Test WebhookEvent enum."""

    def test_events_exist(self):
        """Test that all expected events exist."""
        expected_events = [
            "TODO_CREATED",
            "TODO_UPDATED",
            "TODO_COMPLETED",
            "TODO_DELETED",
            "RECURRENCE_TRIGGERED",
            "REMINDER_DUE"
        ]

        for event in expected_events:
            assert hasattr(WebhookEvent, event)

    def test_event_values(self):
        """Test event string values."""
        assert WebhookEvent.TODO_CREATED == "todo.created"
        assert WebhookEvent.TODO_UPDATED == "todo.updated"
        assert WebhookEvent.TODO_COMPLETED == "todo.completed"
        assert WebhookEvent.TODO_DELETED == "todo.deleted"


class TestWebhookStatus:
    """Test WebhookStatus enum."""

    def test_statuses_exist(self):
        """Test that all statuses exist."""
        assert hasattr(WebhookStatus, "PENDING")
        assert hasattr(WebhookStatus, "DELIVERED")
        assert hasattr(WebhookStatus, "FAILED")
        assert hasattr(WebhookStatus, "RETRYING")

    def test_status_values(self):
        """Test status string values."""
        assert WebhookStatus.PENDING == "pending"
        assert WebhookStatus.DELIVERED == "delivered"
        assert WebhookStatus.FAILED == "failed"
        assert WebhookStatus.RETRYING == "retrying"

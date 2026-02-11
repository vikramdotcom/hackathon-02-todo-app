"""
Tests for Notification System
"""

import pytest
from datetime import datetime
from app.notifications import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationManager,
    EmailProvider,
    SMSProvider,
    PushProvider,
    InAppProvider
)


class TestNotification:
    """Test Notification class."""

    def test_notification_initialization(self):
        """Test notification initialization."""
        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test Notification",
            message="Test message",
            channels=[NotificationChannel.EMAIL],
            priority=NotificationPriority.HIGH
        )

        assert notification.id == "notif-1"
        assert notification.user_id == 123
        assert notification.title == "Test Notification"
        assert notification.message == "Test message"
        assert NotificationChannel.EMAIL in notification.channels
        assert notification.priority == NotificationPriority.HIGH
        assert notification.status == NotificationStatus.PENDING

    def test_notification_with_data(self):
        """Test notification with additional data."""
        data = {"todo_id": 1, "type": "reminder"}

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.PUSH],
            data=data
        )

        assert notification.data == data

    def test_notification_with_action_url(self):
        """Test notification with action URL."""
        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.IN_APP],
            action_url="/todos/1"
        )

        assert notification.action_url == "/todos/1"

    def test_mark_sent(self):
        """Test marking notification as sent."""
        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        result = {"status": "sent", "message_id": "123"}
        notification.mark_sent(NotificationChannel.EMAIL, result)

        assert notification.status == NotificationStatus.SENT
        assert notification.sent_at is not None
        assert NotificationChannel.EMAIL in notification.delivery_results

    def test_mark_delivered(self):
        """Test marking notification as delivered."""
        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        notification.mark_delivered()

        assert notification.status == NotificationStatus.DELIVERED
        assert notification.delivered_at is not None

    def test_mark_read(self):
        """Test marking notification as read."""
        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.IN_APP]
        )

        notification.mark_read()

        assert notification.status == NotificationStatus.READ
        assert notification.read_at is not None

    def test_mark_failed(self):
        """Test marking notification as failed."""
        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        notification.mark_failed("SMTP error")

        assert notification.status == NotificationStatus.FAILED
        assert "error" in notification.delivery_results

    def test_to_dict(self):
        """Test converting notification to dictionary."""
        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH]
        )

        notif_dict = notification.to_dict()

        assert notif_dict["id"] == "notif-1"
        assert notif_dict["user_id"] == 123
        assert notif_dict["title"] == "Test"
        assert "email" in notif_dict["channels"]
        assert "push" in notif_dict["channels"]


class TestEmailProvider:
    """Test EmailProvider class."""

    def test_provider_initialization(self):
        """Test email provider initialization."""
        config = {"host": "smtp.example.com", "port": 587}
        provider = EmailProvider(smtp_config=config)

        assert provider.smtp_config == config

    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test sending email notification."""
        config = {"host": "smtp.example.com"}
        provider = EmailProvider(smtp_config=config)

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        result = await provider.send(notification)

        assert result["channel"] == NotificationChannel.EMAIL
        assert result["status"] == "sent"
        assert "message_id" in result


class TestSMSProvider:
    """Test SMSProvider class."""

    def test_provider_initialization(self):
        """Test SMS provider initialization."""
        provider = SMSProvider(api_key="key123", sender_id="SENDER")

        assert provider.api_key == "key123"
        assert provider.sender_id == "SENDER"

    @pytest.mark.asyncio
    async def test_send_sms(self):
        """Test sending SMS notification."""
        provider = SMSProvider(api_key="key123", sender_id="SENDER")

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.SMS]
        )

        result = await provider.send(notification)

        assert result["channel"] == NotificationChannel.SMS
        assert result["status"] == "sent"


class TestPushProvider:
    """Test PushProvider class."""

    def test_provider_initialization(self):
        """Test push provider initialization."""
        provider = PushProvider(fcm_key="fcm123")

        assert provider.fcm_key == "fcm123"

    @pytest.mark.asyncio
    async def test_send_push(self):
        """Test sending push notification."""
        provider = PushProvider(fcm_key="fcm123")

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.PUSH]
        )

        result = await provider.send(notification)

        assert result["channel"] == NotificationChannel.PUSH
        assert result["status"] == "sent"


class TestInAppProvider:
    """Test InAppProvider class."""

    def test_provider_initialization(self):
        """Test in-app provider initialization."""
        storage = {}
        provider = InAppProvider(storage=storage)

        assert provider.storage == storage

    @pytest.mark.asyncio
    async def test_send_in_app(self):
        """Test storing in-app notification."""
        storage = {}
        provider = InAppProvider(storage=storage)

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.IN_APP]
        )

        result = await provider.send(notification)

        assert result["channel"] == NotificationChannel.IN_APP
        assert result["status"] == "stored"


class TestNotificationManager:
    """Test NotificationManager class."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = NotificationManager()

        assert manager.providers == {}
        assert manager.notifications == {}

    def test_register_provider(self):
        """Test registering a provider."""
        manager = NotificationManager()
        provider = EmailProvider(smtp_config={})

        manager.register_provider(NotificationChannel.EMAIL, provider)

        assert NotificationChannel.EMAIL in manager.providers
        assert manager.providers[NotificationChannel.EMAIL] == provider

    @pytest.mark.asyncio
    async def test_send_notification(self):
        """Test sending notification."""
        manager = NotificationManager()
        provider = EmailProvider(smtp_config={})
        manager.register_provider(NotificationChannel.EMAIL, provider)

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        await manager.send(notification)

        assert notification.id in manager.notifications
        assert notification.status == NotificationStatus.DELIVERED

    @pytest.mark.asyncio
    async def test_send_notification_multiple_channels(self):
        """Test sending notification through multiple channels."""
        manager = NotificationManager()

        email_provider = EmailProvider(smtp_config={})
        push_provider = PushProvider(fcm_key="key")

        manager.register_provider(NotificationChannel.EMAIL, email_provider)
        manager.register_provider(NotificationChannel.PUSH, push_provider)

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH]
        )

        await manager.send(notification)

        assert len(notification.delivery_results) == 2

    def test_get_notification(self):
        """Test getting notification by ID."""
        manager = NotificationManager()

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        manager.notifications[notification.id] = notification

        retrieved = manager.get_notification("notif-1")

        assert retrieved == notification

    def test_get_notification_not_found(self):
        """Test getting non-existent notification."""
        manager = NotificationManager()

        assert manager.get_notification("nonexistent") is None

    def test_get_user_notifications(self):
        """Test getting notifications for user."""
        manager = NotificationManager()

        notif1 = Notification(
            id="notif-1",
            user_id=123,
            title="Test 1",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        notif2 = Notification(
            id="notif-2",
            user_id=123,
            title="Test 2",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        notif3 = Notification(
            id="notif-3",
            user_id=456,
            title="Test 3",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        manager.notifications[notif1.id] = notif1
        manager.notifications[notif2.id] = notif2
        manager.notifications[notif3.id] = notif3

        notifications = manager.get_user_notifications(user_id=123)

        assert len(notifications) == 2
        assert all(n.user_id == 123 for n in notifications)

    def test_get_user_notifications_unread_only(self):
        """Test getting only unread notifications."""
        manager = NotificationManager()

        notif1 = Notification(
            id="notif-1",
            user_id=123,
            title="Test 1",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )
        notif1.mark_read()

        notif2 = Notification(
            id="notif-2",
            user_id=123,
            title="Test 2",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        manager.notifications[notif1.id] = notif1
        manager.notifications[notif2.id] = notif2

        notifications = manager.get_user_notifications(user_id=123, unread_only=True)

        assert len(notifications) == 1
        assert notifications[0].status != NotificationStatus.READ

    def test_mark_as_read(self):
        """Test marking notification as read."""
        manager = NotificationManager()

        notification = Notification(
            id="notif-1",
            user_id=123,
            title="Test",
            message="Test",
            channels=[NotificationChannel.IN_APP]
        )

        manager.notifications[notification.id] = notification

        result = manager.mark_as_read("notif-1")

        assert result is True
        assert notification.status == NotificationStatus.READ

    def test_mark_as_read_not_found(self):
        """Test marking non-existent notification as read."""
        manager = NotificationManager()

        result = manager.mark_as_read("nonexistent")

        assert result is False

    def test_get_unread_count(self):
        """Test getting unread notification count."""
        manager = NotificationManager()

        notif1 = Notification(
            id="notif-1",
            user_id=123,
            title="Test 1",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        notif2 = Notification(
            id="notif-2",
            user_id=123,
            title="Test 2",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )
        notif2.mark_read()

        notif3 = Notification(
            id="notif-3",
            user_id=123,
            title="Test 3",
            message="Test",
            channels=[NotificationChannel.EMAIL]
        )

        manager.notifications[notif1.id] = notif1
        manager.notifications[notif2.id] = notif2
        manager.notifications[notif3.id] = notif3

        count = manager.get_unread_count(user_id=123)

        assert count == 2


class TestNotificationChannel:
    """Test NotificationChannel enum."""

    def test_channels_exist(self):
        """Test that all channels exist."""
        assert hasattr(NotificationChannel, "EMAIL")
        assert hasattr(NotificationChannel, "SMS")
        assert hasattr(NotificationChannel, "PUSH")
        assert hasattr(NotificationChannel, "IN_APP")
        assert hasattr(NotificationChannel, "WEBHOOK")


class TestNotificationPriority:
    """Test NotificationPriority enum."""

    def test_priorities_exist(self):
        """Test that all priorities exist."""
        assert hasattr(NotificationPriority, "LOW")
        assert hasattr(NotificationPriority, "NORMAL")
        assert hasattr(NotificationPriority, "HIGH")
        assert hasattr(NotificationPriority, "URGENT")


class TestNotificationStatus:
    """Test NotificationStatus enum."""

    def test_statuses_exist(self):
        """Test that all statuses exist."""
        assert hasattr(NotificationStatus, "PENDING")
        assert hasattr(NotificationStatus, "SENT")
        assert hasattr(NotificationStatus, "DELIVERED")
        assert hasattr(NotificationStatus, "FAILED")
        assert hasattr(NotificationStatus, "READ")

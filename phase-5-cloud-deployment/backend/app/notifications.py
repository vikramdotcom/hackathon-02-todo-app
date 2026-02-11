"""
Notification System

Provides multi-channel notification delivery (email, SMS, push, in-app).
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Notification delivery status."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification:
    """Notification message."""

    def __init__(
        self,
        id: str,
        user_id: int,
        title: str,
        message: str,
        channels: List[NotificationChannel],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None
    ):
        """
        Initialize notification.

        Args:
            id: Notification ID
            user_id: Target user ID
            title: Notification title
            message: Notification message
            channels: Delivery channels
            priority: Priority level
            data: Additional data
            action_url: Optional action URL
        """
        self.id = id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.channels = channels
        self.priority = priority
        self.data = data or {}
        self.action_url = action_url

        self.status = NotificationStatus.PENDING
        self.created_at = datetime.utcnow()
        self.sent_at: Optional[datetime] = None
        self.delivered_at: Optional[datetime] = None
        self.read_at: Optional[datetime] = None
        self.delivery_results: Dict[str, Any] = {}

    def mark_sent(self, channel: NotificationChannel, result: Dict[str, Any]):
        """Mark notification as sent on channel."""
        self.delivery_results[channel] = result
        if self.status == NotificationStatus.PENDING:
            self.status = NotificationStatus.SENT
            self.sent_at = datetime.utcnow()

    def mark_delivered(self):
        """Mark notification as delivered."""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.utcnow()

    def mark_read(self):
        """Mark notification as read."""
        self.status = NotificationStatus.READ
        self.read_at = datetime.utcnow()

    def mark_failed(self, error: str):
        """Mark notification as failed."""
        self.status = NotificationStatus.FAILED
        self.delivery_results["error"] = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "channels": [c.value for c in self.channels],
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "data": self.data,
            "action_url": self.action_url
        }


class NotificationProvider:
    """Base notification provider."""

    async def send(self, notification: Notification) -> Dict[str, Any]:
        """
        Send notification.

        Args:
            notification: Notification to send

        Returns:
            Delivery result
        """
        raise NotImplementedError


class EmailProvider(NotificationProvider):
    """Email notification provider."""

    def __init__(self, smtp_config: Dict[str, Any]):
        """Initialize email provider."""
        self.smtp_config = smtp_config

    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send email notification."""
        logger.info(
            f"Sending email to user {notification.user_id}",
            extra={
                "notification_id": notification.id,
                "user_id": notification.user_id,
                "title": notification.title
            }
        )

        # Simulate email sending
        # In production, use aiosmtplib or similar
        return {
            "channel": NotificationChannel.EMAIL,
            "status": "sent",
            "message_id": f"email-{notification.id}"
        }


class SMSProvider(NotificationProvider):
    """SMS notification provider."""

    def __init__(self, api_key: str, sender_id: str):
        """Initialize SMS provider."""
        self.api_key = api_key
        self.sender_id = sender_id

    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send SMS notification."""
        logger.info(
            f"Sending SMS to user {notification.user_id}",
            extra={
                "notification_id": notification.id,
                "user_id": notification.user_id
            }
        )

        # Simulate SMS sending
        # In production, use Twilio, AWS SNS, or similar
        return {
            "channel": NotificationChannel.SMS,
            "status": "sent",
            "message_id": f"sms-{notification.id}"
        }


class PushProvider(NotificationProvider):
    """Push notification provider."""

    def __init__(self, fcm_key: str):
        """Initialize push provider."""
        self.fcm_key = fcm_key

    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Send push notification."""
        logger.info(
            f"Sending push notification to user {notification.user_id}",
            extra={
                "notification_id": notification.id,
                "user_id": notification.user_id,
                "title": notification.title
            }
        )

        # Simulate push notification
        # In production, use Firebase Cloud Messaging or similar
        return {
            "channel": NotificationChannel.PUSH,
            "status": "sent",
            "message_id": f"push-{notification.id}"
        }


class InAppProvider(NotificationProvider):
    """In-app notification provider."""

    def __init__(self, storage):
        """Initialize in-app provider."""
        self.storage = storage

    async def send(self, notification: Notification) -> Dict[str, Any]:
        """Store in-app notification."""
        logger.info(
            f"Creating in-app notification for user {notification.user_id}",
            extra={
                "notification_id": notification.id,
                "user_id": notification.user_id
            }
        )

        # Store notification in database
        # In production, save to database
        return {
            "channel": NotificationChannel.IN_APP,
            "status": "stored",
            "notification_id": notification.id
        }


class NotificationManager:
    """Manage notifications across channels."""

    def __init__(self):
        """Initialize notification manager."""
        self.providers: Dict[NotificationChannel, NotificationProvider] = {}
        self.notifications: Dict[str, Notification] = {}

    def register_provider(
        self,
        channel: NotificationChannel,
        provider: NotificationProvider
    ):
        """
        Register notification provider.

        Args:
            channel: Notification channel
            provider: Provider instance
        """
        self.providers[channel] = provider
        logger.info(f"Registered provider for {channel}")

    async def send(self, notification: Notification):
        """
        Send notification through all channels.

        Args:
            notification: Notification to send
        """
        self.notifications[notification.id] = notification

        logger.info(
            f"Sending notification {notification.id}",
            extra={
                "notification_id": notification.id,
                "channels": [c.value for c in notification.channels],
                "priority": notification.priority
            }
        )

        # Send through each channel
        for channel in notification.channels:
            provider = self.providers.get(channel)

            if not provider:
                logger.warning(f"No provider registered for {channel}")
                continue

            try:
                result = await provider.send(notification)
                notification.mark_sent(channel, result)

                logger.info(
                    f"Notification sent via {channel}",
                    extra={
                        "notification_id": notification.id,
                        "channel": channel
                    }
                )

            except Exception as e:
                logger.error(
                    f"Failed to send notification via {channel}: {e}",
                    extra={
                        "notification_id": notification.id,
                        "channel": channel
                    },
                    exc_info=True
                )

        # Mark as delivered if sent successfully on any channel
        if notification.delivery_results:
            notification.mark_delivered()

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        return self.notifications.get(notification_id)

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """
        Get notifications for user.

        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum notifications to return

        Returns:
            List of notifications
        """
        notifications = [
            n for n in self.notifications.values()
            if n.user_id == user_id
        ]

        if unread_only:
            notifications = [
                n for n in notifications
                if n.status != NotificationStatus.READ
            ]

        # Sort by created_at descending
        notifications.sort(key=lambda n: n.created_at, reverse=True)

        return notifications[:limit]

    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark notification as read.

        Args:
            notification_id: Notification ID

        Returns:
            True if marked
        """
        notification = self.notifications.get(notification_id)

        if notification:
            notification.mark_read()
            logger.info(f"Notification {notification_id} marked as read")
            return True

        return False

    def get_unread_count(self, user_id: int) -> int:
        """
        Get unread notification count for user.

        Args:
            user_id: User ID

        Returns:
            Unread count
        """
        return len([
            n for n in self.notifications.values()
            if n.user_id == user_id
            and n.status != NotificationStatus.READ
        ])


# Global notification manager
notification_manager = NotificationManager()


# Helper functions
async def send_todo_reminder(user_id: int, todo_id: int, todo_title: str):
    """Send todo reminder notification."""
    from uuid import uuid4

    notification = Notification(
        id=str(uuid4()),
        user_id=user_id,
        title="Todo Reminder",
        message=f"Reminder: {todo_title}",
        channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        priority=NotificationPriority.HIGH,
        data={"todo_id": todo_id},
        action_url=f"/todos/{todo_id}"
    )

    await notification_manager.send(notification)


async def send_todo_overdue(user_id: int, todo_id: int, todo_title: str):
    """Send todo overdue notification."""
    from uuid import uuid4

    notification = Notification(
        id=str(uuid4()),
        user_id=user_id,
        title="Todo Overdue",
        message=f"Overdue: {todo_title}",
        channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH],
        priority=NotificationPriority.URGENT,
        data={"todo_id": todo_id},
        action_url=f"/todos/{todo_id}"
    )

    await notification_manager.send(notification)

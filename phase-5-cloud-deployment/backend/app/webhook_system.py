"""
Webhook System

Send and receive webhooks for event notifications.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import hmac

logger = logging.getLogger(__name__)


class Webhook:
    """Webhook entity."""

    def __init__(self, url: str, events: List[str], secret: str):
        """Initialize webhook."""
        self.url = url
        self.events = events
        self.secret = secret
        self.active = True
        self.created_at = datetime.utcnow()

    def sign_payload(self, payload: str) -> str:
        """Sign webhook payload."""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()


class WebhookManager:
    """Manage webhooks."""

    def __init__(self):
        """Initialize webhook manager."""
        self.webhooks: Dict[str, Webhook] = {}

    def register_webhook(self, webhook_id: str, url: str, events: List[str], secret: str):
        """Register webhook."""
        webhook = Webhook(url, events, secret)
        self.webhooks[webhook_id] = webhook
        logger.info(f"Webhook registered: {webhook_id}")

    async def send_webhook(self, event: str, payload: Dict[str, Any]):
        """Send webhook for event."""
        for webhook_id, webhook in self.webhooks.items():
            if event in webhook.events and webhook.active:
                logger.info(f"Sending webhook: {webhook_id} for event {event}")


webhook_manager = WebhookManager()

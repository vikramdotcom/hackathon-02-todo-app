"""
Audit Logging System

Provides comprehensive audit logging for security and compliance.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Audit action types."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    PERMISSION_CHANGE = "permission_change"
    CONFIG_CHANGE = "config_change"


class AuditLevel(str, Enum):
    """Audit log levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEntry:
    """Audit log entry."""

    def __init__(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO,
        message: Optional[str] = None
    ):
        """
        Initialize audit entry.

        Args:
            action: Action performed
            resource_type: Type of resource (todo, user, etc.)
            resource_id: Resource identifier
            user_id: User who performed action
            user_email: User email
            ip_address: Client IP address
            user_agent: Client user agent
            changes: Changes made (before/after)
            metadata: Additional metadata
            level: Log level
            message: Human-readable message
        """
        self.timestamp = datetime.utcnow()
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.user_id = user_id
        self.user_email = user_email
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.changes = changes or {}
        self.metadata = metadata or {}
        self.level = level
        self.message = message or self._generate_message()

    def _generate_message(self) -> str:
        """Generate human-readable message."""
        user = self.user_email or f"User {self.user_id}" or "Unknown user"
        resource = f"{self.resource_type}"
        if self.resource_id:
            resource += f" {self.resource_id}"

        return f"{user} performed {self.action} on {resource}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "changes": self.changes,
            "metadata": self.metadata,
            "level": self.level,
            "message": self.message
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class AuditLogger:
    """Audit logging manager."""

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize audit logger.

        Args:
            storage_backend: Optional storage backend for persistence
        """
        self.storage_backend = storage_backend
        self.entries = []

    def log(self, entry: AuditEntry):
        """
        Log audit entry.

        Args:
            entry: AuditEntry instance
        """
        # Add to in-memory list
        self.entries.append(entry)

        # Log to standard logger
        log_method = getattr(logger, entry.level.value)
        log_method(
            entry.message,
            extra={
                "audit": True,
                "action": entry.action,
                "resource_type": entry.resource_type,
                "resource_id": entry.resource_id,
                "user_id": entry.user_id
            }
        )

        # Persist to storage backend if available
        if self.storage_backend:
            try:
                self.storage_backend.save(entry)
            except Exception as e:
                logger.error(f"Failed to persist audit entry: {e}", exc_info=True)

    def log_create(
        self,
        resource_type: str,
        resource_id: str,
        user_id: Optional[int] = None,
        **kwargs
    ):
        """Log resource creation."""
        entry = AuditEntry(
            action=AuditAction.CREATE,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            **kwargs
        )
        self.log(entry)

    def log_update(
        self,
        resource_type: str,
        resource_id: str,
        changes: Dict[str, Any],
        user_id: Optional[int] = None,
        **kwargs
    ):
        """Log resource update."""
        entry = AuditEntry(
            action=AuditAction.UPDATE,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            changes=changes,
            **kwargs
        )
        self.log(entry)

    def log_delete(
        self,
        resource_type: str,
        resource_id: str,
        user_id: Optional[int] = None,
        **kwargs
    ):
        """Log resource deletion."""
        entry = AuditEntry(
            action=AuditAction.DELETE,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            level=AuditLevel.WARNING,
            **kwargs
        )
        self.log(entry)

    def log_login(
        self,
        user_id: int,
        user_email: str,
        ip_address: Optional[str] = None,
        success: bool = True,
        **kwargs
    ):
        """Log user login."""
        entry = AuditEntry(
            action=AuditAction.LOGIN,
            resource_type="user",
            resource_id=str(user_id),
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            level=AuditLevel.INFO if success else AuditLevel.WARNING,
            message=f"User {user_email} {'logged in' if success else 'failed login'}",
            **kwargs
        )
        self.log(entry)

    def log_permission_change(
        self,
        user_id: int,
        changes: Dict[str, Any],
        performed_by: Optional[int] = None,
        **kwargs
    ):
        """Log permission changes."""
        entry = AuditEntry(
            action=AuditAction.PERMISSION_CHANGE,
            resource_type="user",
            resource_id=str(user_id),
            user_id=performed_by,
            changes=changes,
            level=AuditLevel.WARNING,
            **kwargs
        )
        self.log(entry)

    def get_entries(
        self,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> list[AuditEntry]:
        """
        Query audit entries.

        Args:
            user_id: Filter by user ID
            resource_type: Filter by resource type
            action: Filter by action
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum entries to return

        Returns:
            List of matching audit entries
        """
        filtered = self.entries

        if user_id is not None:
            filtered = [e for e in filtered if e.user_id == user_id]

        if resource_type is not None:
            filtered = [e for e in filtered if e.resource_type == resource_type]

        if action is not None:
            filtered = [e for e in filtered if e.action == action]

        if start_time is not None:
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if end_time is not None:
            filtered = [e for e in filtered if e.timestamp <= end_time]

        # Sort by timestamp descending
        filtered.sort(key=lambda e: e.timestamp, reverse=True)

        return filtered[:limit]

    def export_entries(
        self,
        format: str = "json",
        **filters
    ) -> str:
        """
        Export audit entries.

        Args:
            format: Export format (json, csv)
            **filters: Query filters

        Returns:
            Exported data as string
        """
        entries = self.get_entries(**filters)

        if format == "json":
            return json.dumps([e.to_dict() for e in entries], indent=2)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            if entries:
                writer = csv.DictWriter(output, fieldnames=entries[0].to_dict().keys())
                writer.writeheader()
                for entry in entries:
                    writer.writerow(entry.to_dict())

            return output.getvalue()

        else:
            raise ValueError(f"Unsupported format: {format}")


# Global audit logger instance
audit_logger = AuditLogger()


# Decorator for automatic audit logging
def audit_log(
    action: AuditAction,
    resource_type: str,
    get_resource_id: Optional[callable] = None
):
    """
    Decorator for automatic audit logging.

    Args:
        action: Audit action
        resource_type: Resource type
        get_resource_id: Function to extract resource ID from result

    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Extract resource ID if function provided
            resource_id = None
            if get_resource_id and result:
                try:
                    resource_id = get_resource_id(result)
                except Exception:
                    pass

            # Create audit entry
            entry = AuditEntry(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id
            )

            audit_logger.log(entry)

            return result

        return wrapper
    return decorator

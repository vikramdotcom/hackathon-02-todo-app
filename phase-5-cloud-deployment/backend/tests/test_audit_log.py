"""
Tests for Audit Logging System
"""

import pytest
from datetime import datetime, timedelta
from app.audit_log import (
    AuditEntry,
    AuditAction,
    AuditLevel,
    AuditLogger,
    audit_log
)


class TestAuditEntry:
    """Test AuditEntry class."""

    def test_entry_initialization(self):
        """Test audit entry initialization."""
        entry = AuditEntry(
            action=AuditAction.CREATE,
            resource_type="todo",
            resource_id="1",
            user_id=123,
            user_email="user@example.com"
        )

        assert entry.action == AuditAction.CREATE
        assert entry.resource_type == "todo"
        assert entry.resource_id == "1"
        assert entry.user_id == 123
        assert entry.user_email == "user@example.com"
        assert entry.level == AuditLevel.INFO
        assert entry.timestamp is not None

    def test_entry_with_changes(self):
        """Test entry with change tracking."""
        changes = {
            "title": {"before": "Old", "after": "New"},
            "completed": {"before": False, "after": True}
        }

        entry = AuditEntry(
            action=AuditAction.UPDATE,
            resource_type="todo",
            resource_id="1",
            changes=changes
        )

        assert entry.changes == changes

    def test_entry_with_metadata(self):
        """Test entry with metadata."""
        metadata = {"source": "api", "version": "2.0"}

        entry = AuditEntry(
            action=AuditAction.CREATE,
            resource_type="todo",
            metadata=metadata
        )

        assert entry.metadata == metadata

    def test_entry_message_generation(self):
        """Test automatic message generation."""
        entry = AuditEntry(
            action=AuditAction.UPDATE,
            resource_type="todo",
            resource_id="1",
            user_email="user@example.com"
        )

        assert "user@example.com" in entry.message
        assert "update" in entry.message.lower()
        assert "todo" in entry.message.lower()

    def test_entry_custom_message(self):
        """Test custom message."""
        custom_message = "Custom audit message"

        entry = AuditEntry(
            action=AuditAction.CREATE,
            resource_type="todo",
            message=custom_message
        )

        assert entry.message == custom_message

    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        entry = AuditEntry(
            action=AuditAction.CREATE,
            resource_type="todo",
            resource_id="1",
            user_id=123
        )

        entry_dict = entry.to_dict()

        assert "timestamp" in entry_dict
        assert entry_dict["action"] == AuditAction.CREATE
        assert entry_dict["resource_type"] == "todo"
        assert entry_dict["resource_id"] == "1"
        assert entry_dict["user_id"] == 123

    def test_entry_to_json(self):
        """Test converting entry to JSON."""
        entry = AuditEntry(
            action=AuditAction.CREATE,
            resource_type="todo",
            resource_id="1"
        )

        json_str = entry.to_json()

        assert isinstance(json_str, str)
        assert "todo" in json_str
        assert "create" in json_str

    def test_entry_with_ip_and_user_agent(self):
        """Test entry with IP and user agent."""
        entry = AuditEntry(
            action=AuditAction.LOGIN,
            resource_type="user",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        assert entry.ip_address == "192.168.1.1"
        assert entry.user_agent == "Mozilla/5.0"


class TestAuditLogger:
    """Test AuditLogger class."""

    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = AuditLogger()

        assert logger.entries == []
        assert logger.storage_backend is None

    def test_log_entry(self):
        """Test logging an entry."""
        logger = AuditLogger()

        entry = AuditEntry(
            action=AuditAction.CREATE,
            resource_type="todo",
            resource_id="1"
        )

        logger.log(entry)

        assert len(logger.entries) == 1
        assert logger.entries[0] == entry

    def test_log_create(self):
        """Test logging create action."""
        logger = AuditLogger()

        logger.log_create(
            resource_type="todo",
            resource_id="1",
            user_id=123
        )

        assert len(logger.entries) == 1
        assert logger.entries[0].action == AuditAction.CREATE
        assert logger.entries[0].resource_type == "todo"
        assert logger.entries[0].resource_id == "1"

    def test_log_update(self):
        """Test logging update action."""
        logger = AuditLogger()

        changes = {"title": {"before": "Old", "after": "New"}}

        logger.log_update(
            resource_type="todo",
            resource_id="1",
            changes=changes,
            user_id=123
        )

        assert len(logger.entries) == 1
        assert logger.entries[0].action == AuditAction.UPDATE
        assert logger.entries[0].changes == changes

    def test_log_delete(self):
        """Test logging delete action."""
        logger = AuditLogger()

        logger.log_delete(
            resource_type="todo",
            resource_id="1",
            user_id=123
        )

        assert len(logger.entries) == 1
        assert logger.entries[0].action == AuditAction.DELETE
        assert logger.entries[0].level == AuditLevel.WARNING

    def test_log_login_success(self):
        """Test logging successful login."""
        logger = AuditLogger()

        logger.log_login(
            user_id=123,
            user_email="user@example.com",
            ip_address="192.168.1.1",
            success=True
        )

        assert len(logger.entries) == 1
        assert logger.entries[0].action == AuditAction.LOGIN
        assert logger.entries[0].level == AuditLevel.INFO
        assert "logged in" in logger.entries[0].message

    def test_log_login_failure(self):
        """Test logging failed login."""
        logger = AuditLogger()

        logger.log_login(
            user_id=123,
            user_email="user@example.com",
            ip_address="192.168.1.1",
            success=False
        )

        assert len(logger.entries) == 1
        assert logger.entries[0].level == AuditLevel.WARNING
        assert "failed login" in logger.entries[0].message

    def test_log_permission_change(self):
        """Test logging permission changes."""
        logger = AuditLogger()

        changes = {"role": {"before": "user", "after": "admin"}}

        logger.log_permission_change(
            user_id=123,
            changes=changes,
            performed_by=456
        )

        assert len(logger.entries) == 1
        assert logger.entries[0].action == AuditAction.PERMISSION_CHANGE
        assert logger.entries[0].level == AuditLevel.WARNING
        assert logger.entries[0].user_id == 456

    def test_get_entries_no_filter(self):
        """Test getting all entries."""
        logger = AuditLogger()

        logger.log_create("todo", "1", user_id=123)
        logger.log_update("todo", "1", {"title": {}}, user_id=123)
        logger.log_delete("todo", "1", user_id=123)

        entries = logger.get_entries()

        assert len(entries) == 3

    def test_get_entries_filter_by_user(self):
        """Test filtering entries by user."""
        logger = AuditLogger()

        logger.log_create("todo", "1", user_id=123)
        logger.log_create("todo", "2", user_id=456)
        logger.log_create("todo", "3", user_id=123)

        entries = logger.get_entries(user_id=123)

        assert len(entries) == 2
        assert all(e.user_id == 123 for e in entries)

    def test_get_entries_filter_by_resource_type(self):
        """Test filtering entries by resource type."""
        logger = AuditLogger()

        logger.log_create("todo", "1")
        logger.log_create("user", "1")
        logger.log_create("todo", "2")

        entries = logger.get_entries(resource_type="todo")

        assert len(entries) == 2
        assert all(e.resource_type == "todo" for e in entries)

    def test_get_entries_filter_by_action(self):
        """Test filtering entries by action."""
        logger = AuditLogger()

        logger.log_create("todo", "1")
        logger.log_update("todo", "1", {})
        logger.log_create("todo", "2")

        entries = logger.get_entries(action=AuditAction.CREATE)

        assert len(entries) == 2
        assert all(e.action == AuditAction.CREATE for e in entries)

    def test_get_entries_filter_by_time_range(self):
        """Test filtering entries by time range."""
        logger = AuditLogger()

        # Create entries with different timestamps
        entry1 = AuditEntry(action=AuditAction.CREATE, resource_type="todo", resource_id="1")
        entry1.timestamp = datetime.utcnow() - timedelta(hours=2)

        entry2 = AuditEntry(action=AuditAction.CREATE, resource_type="todo", resource_id="2")
        entry2.timestamp = datetime.utcnow() - timedelta(hours=1)

        entry3 = AuditEntry(action=AuditAction.CREATE, resource_type="todo", resource_id="3")
        entry3.timestamp = datetime.utcnow()

        logger.log(entry1)
        logger.log(entry2)
        logger.log(entry3)

        # Filter by start time
        start_time = datetime.utcnow() - timedelta(hours=1, minutes=30)
        entries = logger.get_entries(start_time=start_time)

        assert len(entries) == 2

    def test_get_entries_limit(self):
        """Test limiting number of entries returned."""
        logger = AuditLogger()

        for i in range(10):
            logger.log_create("todo", str(i))

        entries = logger.get_entries(limit=5)

        assert len(entries) == 5

    def test_get_entries_sorted_by_timestamp(self):
        """Test entries are sorted by timestamp descending."""
        logger = AuditLogger()

        logger.log_create("todo", "1")
        logger.log_create("todo", "2")
        logger.log_create("todo", "3")

        entries = logger.get_entries()

        # Most recent first
        for i in range(len(entries) - 1):
            assert entries[i].timestamp >= entries[i + 1].timestamp

    def test_export_entries_json(self):
        """Test exporting entries as JSON."""
        logger = AuditLogger()

        logger.log_create("todo", "1", user_id=123)
        logger.log_update("todo", "1", {"title": {}}, user_id=123)

        json_export = logger.export_entries(format="json")

        assert isinstance(json_export, str)
        assert "todo" in json_export
        assert "create" in json_export
        assert "update" in json_export

    def test_export_entries_csv(self):
        """Test exporting entries as CSV."""
        logger = AuditLogger()

        logger.log_create("todo", "1", user_id=123)
        logger.log_update("todo", "1", {"title": {}}, user_id=123)

        csv_export = logger.export_entries(format="csv")

        assert isinstance(csv_export, str)
        assert "timestamp" in csv_export
        assert "action" in csv_export
        assert "resource_type" in csv_export

    def test_export_entries_invalid_format(self):
        """Test exporting with invalid format."""
        logger = AuditLogger()

        logger.log_create("todo", "1")

        with pytest.raises(ValueError):
            logger.export_entries(format="invalid")

    def test_export_entries_with_filters(self):
        """Test exporting filtered entries."""
        logger = AuditLogger()

        logger.log_create("todo", "1", user_id=123)
        logger.log_create("todo", "2", user_id=456)
        logger.log_create("user", "1", user_id=123)

        json_export = logger.export_entries(
            format="json",
            resource_type="todo",
            user_id=123
        )

        assert "todo" in json_export
        # Should only include one entry (todo created by user 123)


class TestAuditLogDecorator:
    """Test audit_log decorator."""

    def test_decorator_logs_action(self):
        """Test decorator logs action."""
        logger = AuditLogger()

        @audit_log(AuditAction.CREATE, "todo")
        def create_todo():
            return {"id": 1, "title": "Test"}

        # Replace global logger temporarily
        import app.audit_log as audit_module
        original_logger = audit_module.audit_logger
        audit_module.audit_logger = logger

        try:
            result = create_todo()

            assert result["id"] == 1
            assert len(logger.entries) == 1
            assert logger.entries[0].action == AuditAction.CREATE
            assert logger.entries[0].resource_type == "todo"
        finally:
            audit_module.audit_logger = original_logger

    def test_decorator_with_resource_id_extractor(self):
        """Test decorator with resource ID extraction."""
        logger = AuditLogger()

        @audit_log(
            AuditAction.CREATE,
            "todo",
            get_resource_id=lambda result: str(result["id"])
        )
        def create_todo():
            return {"id": 1, "title": "Test"}

        import app.audit_log as audit_module
        original_logger = audit_module.audit_logger
        audit_module.audit_logger = logger

        try:
            create_todo()

            assert len(logger.entries) == 1
            assert logger.entries[0].resource_id == "1"
        finally:
            audit_module.audit_logger = original_logger


class TestAuditAction:
    """Test AuditAction enum."""

    def test_actions_exist(self):
        """Test that all expected actions exist."""
        expected_actions = [
            "CREATE", "READ", "UPDATE", "DELETE",
            "LOGIN", "LOGOUT", "EXPORT", "IMPORT",
            "PERMISSION_CHANGE", "CONFIG_CHANGE"
        ]

        for action in expected_actions:
            assert hasattr(AuditAction, action)

    def test_action_values(self):
        """Test action string values."""
        assert AuditAction.CREATE == "create"
        assert AuditAction.UPDATE == "update"
        assert AuditAction.DELETE == "delete"
        assert AuditAction.LOGIN == "login"


class TestAuditLevel:
    """Test AuditLevel enum."""

    def test_levels_exist(self):
        """Test that all levels exist."""
        assert hasattr(AuditLevel, "INFO")
        assert hasattr(AuditLevel, "WARNING")
        assert hasattr(AuditLevel, "ERROR")
        assert hasattr(AuditLevel, "CRITICAL")

    def test_level_values(self):
        """Test level string values."""
        assert AuditLevel.INFO == "info"
        assert AuditLevel.WARNING == "warning"
        assert AuditLevel.ERROR == "error"
        assert AuditLevel.CRITICAL == "critical"

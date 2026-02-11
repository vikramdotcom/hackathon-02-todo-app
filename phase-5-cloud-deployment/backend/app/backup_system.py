"""
Backup and Restore System

Handle database backups and restoration.
"""

import logging
import json
import gzip
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class BackupMetadata:
    """Backup metadata."""

    def __init__(
        self,
        backup_id: str,
        backup_type: str,
        size_bytes: int,
        checksum: str
    ):
        """Initialize backup metadata."""
        self.backup_id = backup_id
        self.backup_type = backup_type
        self.size_bytes = size_bytes
        self.checksum = checksum
        self.created_at = datetime.utcnow()
        self.status = "completed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "backup_id": self.backup_id,
            "backup_type": self.backup_type,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }


class BackupManager:
    """Manage database backups."""

    def __init__(self, backup_dir: str = "backups"):
        """Initialize backup manager."""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backups: List[BackupMetadata] = []

    def create_backup(
        self,
        data: Dict[str, Any],
        backup_type: str = "full",
        compress: bool = True
    ) -> BackupMetadata:
        """Create backup."""
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        filename = f"{backup_id}.json"

        if compress:
            filename += ".gz"

        filepath = self.backup_dir / filename

        # Serialize data
        json_data = json.dumps(data, indent=2)

        # Calculate checksum
        checksum = hashlib.sha256(json_data.encode()).hexdigest()

        # Write backup
        if compress:
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                f.write(json_data)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_data)

        size_bytes = filepath.stat().st_size

        metadata = BackupMetadata(backup_id, backup_type, size_bytes, checksum)
        self.backups.append(metadata)

        logger.info(
            f"Created backup: {backup_id}",
            extra={
                "backup_id": backup_id,
                "type": backup_type,
                "size": size_bytes,
                "compressed": compress
            }
        )

        return metadata

    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore from backup."""
        # Find backup file
        json_file = self.backup_dir / f"{backup_id}.json"
        gz_file = self.backup_dir / f"{backup_id}.json.gz"

        filepath = None
        compressed = False

        if gz_file.exists():
            filepath = gz_file
            compressed = True
        elif json_file.exists():
            filepath = json_file

        if not filepath:
            raise FileNotFoundError(f"Backup not found: {backup_id}")

        # Read backup
        if compressed:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                json_data = f.read()
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = f.read()

        data = json.loads(json_data)

        logger.info(f"Restored backup: {backup_id}")

        return data

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all backups."""
        return [b.to_dict() for b in self.backups]

    def delete_backup(self, backup_id: str):
        """Delete backup."""
        # Delete files
        json_file = self.backup_dir / f"{backup_id}.json"
        gz_file = self.backup_dir / f"{backup_id}.json.gz"

        if gz_file.exists():
            gz_file.unlink()
        if json_file.exists():
            json_file.unlink()

        # Remove from list
        self.backups = [b for b in self.backups if b.backup_id != backup_id]

        logger.info(f"Deleted backup: {backup_id}")

    def cleanup_old_backups(self, keep_count: int = 10):
        """Cleanup old backups."""
        if len(self.backups) <= keep_count:
            return

        # Sort by creation date
        sorted_backups = sorted(self.backups, key=lambda b: b.created_at, reverse=True)

        # Delete old backups
        to_delete = sorted_backups[keep_count:]

        for backup in to_delete:
            self.delete_backup(backup.backup_id)

        logger.info(f"Cleaned up {len(to_delete)} old backups")


class IncrementalBackup:
    """Handle incremental backups."""

    def __init__(self, backup_manager: BackupManager):
        """Initialize incremental backup."""
        self.backup_manager = backup_manager
        self.last_backup_data: Optional[Dict[str, Any]] = None

    def create_incremental_backup(self, current_data: Dict[str, Any]) -> BackupMetadata:
        """Create incremental backup."""
        if not self.last_backup_data:
            # First backup is full
            metadata = self.backup_manager.create_backup(current_data, "full")
            self.last_backup_data = current_data
            return metadata

        # Calculate changes
        changes = self._calculate_changes(self.last_backup_data, current_data)

        # Create incremental backup
        metadata = self.backup_manager.create_backup(changes, "incremental")
        self.last_backup_data = current_data

        return metadata

    def _calculate_changes(
        self,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate changes between datasets."""
        changes = {
            "added": {},
            "modified": {},
            "deleted": {}
        }

        # Find added and modified
        for key, value in new_data.items():
            if key not in old_data:
                changes["added"][key] = value
            elif old_data[key] != value:
                changes["modified"][key] = value

        # Find deleted
        for key in old_data:
            if key not in new_data:
                changes["deleted"][key] = old_data[key]

        return changes


class BackupScheduler:
    """Schedule automated backups."""

    def __init__(self, backup_manager: BackupManager):
        """Initialize backup scheduler."""
        self.backup_manager = backup_manager
        self.schedules: List[Dict[str, Any]] = []

    def schedule_backup(
        self,
        name: str,
        frequency: str,
        backup_type: str = "full",
        retention_days: int = 30
    ):
        """Schedule backup."""
        schedule = {
            "name": name,
            "frequency": frequency,
            "backup_type": backup_type,
            "retention_days": retention_days,
            "last_run": None,
            "next_run": None
        }

        self.schedules.append(schedule)

        logger.info(
            f"Scheduled backup: {name}",
            extra={"name": name, "frequency": frequency}
        )

    def get_due_backups(self) -> List[Dict[str, Any]]:
        """Get backups that are due."""
        # In production, implement proper scheduling logic
        return []


class RestoreValidator:
    """Validate backup before restoration."""

    def __init__(self):
        """Initialize restore validator."""
        pass

    def validate_backup(self, backup_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate backup data."""
        errors = []

        # Check required fields
        if "version" not in backup_data:
            errors.append("Missing version field")

        if "data" not in backup_data:
            errors.append("Missing data field")

        # Check data integrity
        if "data" in backup_data:
            data = backup_data["data"]

            if not isinstance(data, dict):
                errors.append("Data must be a dictionary")

        return len(errors) == 0, errors

    def validate_compatibility(
        self,
        backup_version: str,
        current_version: str
    ) -> tuple[bool, Optional[str]]:
        """Validate version compatibility."""
        # Simple version check
        if backup_version == current_version:
            return True, None

        # Check if migration is needed
        return False, f"Version mismatch: backup={backup_version}, current={current_version}"


class BackupEncryption:
    """Encrypt backups for security."""

    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize backup encryption."""
        self.encryption_key = encryption_key

    def encrypt_backup(self, data: bytes) -> bytes:
        """Encrypt backup data."""
        # In production, use proper encryption library
        # This is a simplified example
        import base64
        return base64.b64encode(data)

    def decrypt_backup(self, encrypted_data: bytes) -> bytes:
        """Decrypt backup data."""
        # In production, use proper encryption library
        import base64
        return base64.b64decode(encrypted_data)


class DisasterRecovery:
    """Disaster recovery utilities."""

    def __init__(self, backup_manager: BackupManager):
        """Initialize disaster recovery."""
        self.backup_manager = backup_manager

    def create_recovery_point(self, data: Dict[str, Any]) -> str:
        """Create recovery point."""
        metadata = self.backup_manager.create_backup(data, "recovery_point")
        return metadata.backup_id

    def restore_to_recovery_point(self, backup_id: str) -> Dict[str, Any]:
        """Restore to recovery point."""
        return self.backup_manager.restore_backup(backup_id)

    def verify_recovery_capability(self) -> Dict[str, Any]:
        """Verify disaster recovery capability."""
        backups = self.backup_manager.list_backups()

        return {
            "total_backups": len(backups),
            "latest_backup": backups[-1] if backups else None,
            "recovery_ready": len(backups) > 0
        }


# Global instances
backup_manager = BackupManager()
incremental_backup = IncrementalBackup(backup_manager)
backup_scheduler = BackupScheduler(backup_manager)
restore_validator = RestoreValidator()
disaster_recovery = DisasterRecovery(backup_manager)


# Helper functions
def create_backup(data: Dict[str, Any], compress: bool = True) -> BackupMetadata:
    """Create backup."""
    return backup_manager.create_backup(data, compress=compress)


def restore_backup(backup_id: str) -> Dict[str, Any]:
    """Restore backup."""
    return backup_manager.restore_backup(backup_id)


def list_backups() -> List[Dict[str, Any]]:
    """List all backups."""
    return backup_manager.list_backups()

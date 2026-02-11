"""
Database Backup and Restore Script

Provides utilities for backing up and restoring the database.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Database backup and restore utilities."""

    def __init__(self, database_url: str):
        """
        Initialize database backup.

        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, backup_name: str = None) -> str:
        """
        Create a database backup.

        Args:
            backup_name: Optional backup name (defaults to timestamp)

        Returns:
            Path to backup file
        """
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.sql"

        backup_path = self.backup_dir / backup_name

        print(f"Creating backup: {backup_path}")

        try:
            # Use pg_dump to create backup
            cmd = f"pg_dump {self.database_url} > {backup_path}"
            subprocess.run(cmd, shell=True, check=True)

            # Compress backup
            compressed_path = f"{backup_path}.gz"
            subprocess.run(f"gzip {backup_path}", shell=True, check=True)

            print(f"✓ Backup created: {compressed_path}")
            return str(compressed_path)

        except subprocess.CalledProcessError as e:
            print(f"✗ Backup failed: {e}")
            raise

    def restore_backup(self, backup_path: str):
        """
        Restore database from backup.

        Args:
            backup_path: Path to backup file
        """
        print(f"Restoring from backup: {backup_path}")

        try:
            # Decompress if needed
            if backup_path.endswith(".gz"):
                subprocess.run(f"gunzip -k {backup_path}", shell=True, check=True)
                backup_path = backup_path[:-3]

            # Restore database
            cmd = f"psql {self.database_url} < {backup_path}"
            subprocess.run(cmd, shell=True, check=True)

            print(f"✓ Database restored from {backup_path}")

        except subprocess.CalledProcessError as e:
            print(f"✗ Restore failed: {e}")
            raise

    def list_backups(self) -> list:
        """
        List available backups.

        Returns:
            List of backup files
        """
        backups = sorted(self.backup_dir.glob("*.sql.gz"), reverse=True)
        return [str(b) for b in backups]

    def cleanup_old_backups(self, keep_count: int = 10):
        """
        Remove old backups, keeping only the most recent.

        Args:
            keep_count: Number of backups to keep
        """
        backups = self.list_backups()

        if len(backups) > keep_count:
            to_remove = backups[keep_count:]
            print(f"Removing {len(to_remove)} old backups...")

            for backup in to_remove:
                os.remove(backup)
                print(f"  Removed: {backup}")

            print(f"✓ Kept {keep_count} most recent backups")


def main():
    """Main backup script."""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_database.py backup [name]")
        print("  python backup_database.py restore <backup_file>")
        print("  python backup_database.py list")
        print("  python backup_database.py cleanup [keep_count]")
        sys.exit(1)

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)

    backup = DatabaseBackup(database_url)
    command = sys.argv[1]

    if command == "backup":
        backup_name = sys.argv[2] if len(sys.argv) > 2 else None
        backup.create_backup(backup_name)

    elif command == "restore":
        if len(sys.argv) < 3:
            print("Error: Backup file path required")
            sys.exit(1)
        backup.restore_backup(sys.argv[2])

    elif command == "list":
        backups = backup.list_backups()
        print(f"\nAvailable backups ({len(backups)}):")
        for b in backups:
            print(f"  {b}")

    elif command == "cleanup":
        keep_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        backup.cleanup_old_backups(keep_count)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

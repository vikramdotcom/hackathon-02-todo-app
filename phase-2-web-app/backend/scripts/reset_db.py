#!/usr/bin/env python3
"""
Database reset script for clean deployment.
Removes old database and runs fresh migrations.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from app.core.config import settings


def reset_database():
    """Reset database by removing old file and running fresh migrations."""
    print("[*] Starting database reset...")

    # Extract database file path from DATABASE_URL
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")

        # Remove old database file if it exists
        if os.path.exists(db_path):
            print(f"[*] Removing old database: {db_path}")
            os.remove(db_path)
            print("[+] Old database removed")
        else:
            print(f"[i] No existing database found at: {db_path}")

    # Run fresh migrations
    print("\n[*] Running fresh migrations...")
    alembic_cfg = Config("alembic.ini")

    try:
        # Run upgrade to head
        command.upgrade(alembic_cfg, "head")
        print("[+] Migrations completed successfully")
        print("\n[+] Database reset complete! Ready for deployment.")
        return True
    except Exception as e:
        print(f"[-] Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)

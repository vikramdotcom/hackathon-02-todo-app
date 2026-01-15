"""
Startup utilities for database initialization with error handling.
Ensures clean database state on deployment.
"""
import os
import logging
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import inspect, text
from app.core.database import engine
from app.core.config import settings

logger = logging.getLogger(__name__)


def check_database_health() -> bool:
    """
    Check if database is healthy and migrations are applied.
    Returns True if database is ready, False if needs reset.
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Check if required tables exist
        required_tables = ['users', 'todos', 'alembic_version']
        if not all(table in tables for table in required_tables):
            logger.warning("Missing required tables")
            return False

        # Check if users table has correct structure (no broken constraints)
        with engine.connect() as conn:
            # Try a simple query to verify table is accessible
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            result.fetchone()

        logger.info("Database health check passed")
        return True

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def reset_database_if_needed():
    """
    Reset database if it's corrupted or has migration issues.
    Only for SQLite databases.
    """
    db_url = settings.DATABASE_URL

    if not db_url.startswith("sqlite:///"):
        logger.info("Non-SQLite database detected, skipping reset check")
        return

    # Check database health
    if check_database_health():
        logger.info("Database is healthy, no reset needed")
        return

    logger.warning("Database health check failed, attempting reset...")

    # Extract database file path
    db_path = db_url.replace("sqlite:///", "")

    # Remove corrupted database
    if os.path.exists(db_path):
        logger.info(f"Removing corrupted database: {db_path}")
        try:
            os.remove(db_path)
            logger.info("Corrupted database removed")
        except Exception as e:
            logger.error(f"Failed to remove database: {e}")
            raise

    # Run fresh migrations
    logger.info("Running fresh migrations...")
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Fresh migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


def initialize_database():
    """
    Initialize database on startup with error handling.
    Safe for Hugging Face Spaces deployment.
    """
    try:
        logger.info("Starting database initialization...")
        reset_database_if_needed()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Re-raise to prevent app from starting with broken database
        raise RuntimeError(f"Failed to initialize database: {e}")

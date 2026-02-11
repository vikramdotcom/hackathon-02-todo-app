"""
Database Configuration and Session Management

Provides database connection, session management, and dependency injection
for FastAPI endpoints.
"""

from typing import Generator
from sqlmodel import Session, create_engine
from contextlib import contextmanager
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/todo_db"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Yields a database session and ensures it's closed after use.
    Automatically commits on success, rolls back on error.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.exec(select(Item)).all()
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI.

    Usage:
        with get_db_context() as db:
            todos = db.exec(select(Todo)).all()
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database context error: {e}")
        raise
    finally:
        session.close()


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in SQLModel metadata.
    Should be called on application startup.
    """
    from sqlmodel import SQLModel
    from app.models.todo import Todo
    from app.models.recurrence import RecurrencePattern

    logger.info("Initializing database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables initialized successfully")


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_db_context() as db:
            db.exec("SELECT 1")
        logger.info("Database connection check: OK")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

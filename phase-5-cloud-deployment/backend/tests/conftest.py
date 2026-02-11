"""
Pytest Configuration and Fixtures

Provides shared test fixtures for database, API client, and test data.
"""

import pytest
from typing import Generator
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models.todo import Todo, TodoPriority
from app.models.recurrence import RecurrencePattern, RecurrenceFrequency, RecurrenceEndCondition
from datetime import datetime, timedelta


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(name="engine")
def engine_fixture():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture(name="sample_user_id")
def sample_user_id_fixture() -> int:
    """Return a sample user ID for testing."""
    return 1


@pytest.fixture(name="sample_todo")
def sample_todo_fixture(session: Session, sample_user_id: int) -> Todo:
    """Create a sample todo for testing."""
    todo = Todo(
        title="Test Todo",
        description="This is a test todo",
        user_id=sample_user_id,
        priority=TodoPriority.MEDIUM,
        tags=["test", "sample"],
        completed=False
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@pytest.fixture(name="sample_todo_with_due_date")
def sample_todo_with_due_date_fixture(session: Session, sample_user_id: int) -> Todo:
    """Create a sample todo with due date for testing."""
    todo = Todo(
        title="Todo with Due Date",
        description="This todo has a due date",
        user_id=sample_user_id,
        priority=TodoPriority.HIGH,
        due_date=datetime.utcnow() + timedelta(days=7),
        tags=["urgent"],
        completed=False
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@pytest.fixture(name="sample_overdue_todo")
def sample_overdue_todo_fixture(session: Session, sample_user_id: int) -> Todo:
    """Create a sample overdue todo for testing."""
    todo = Todo(
        title="Overdue Todo",
        description="This todo is overdue",
        user_id=sample_user_id,
        priority=TodoPriority.URGENT,
        due_date=datetime.utcnow() - timedelta(days=2),
        completed=False
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@pytest.fixture(name="sample_recurrence_pattern")
def sample_recurrence_pattern_fixture(session: Session) -> RecurrencePattern:
    """Create a sample recurrence pattern for testing."""
    pattern = RecurrencePattern(
        frequency=RecurrenceFrequency.WEEKLY,
        interval=1,
        end_condition=RecurrenceEndCondition.NEVER,
        next_occurrence=datetime.utcnow() + timedelta(days=7),
        occurrence_count=0,
        days_of_week=[0, 2, 4]  # Monday, Wednesday, Friday
    )
    session.add(pattern)
    session.commit()
    session.refresh(pattern)
    return pattern


@pytest.fixture(name="sample_recurring_todo")
def sample_recurring_todo_fixture(
    session: Session,
    sample_user_id: int,
    sample_recurrence_pattern: RecurrencePattern
) -> Todo:
    """Create a sample recurring todo for testing."""
    todo = Todo(
        title="Recurring Todo",
        description="This todo recurs weekly",
        user_id=sample_user_id,
        priority=TodoPriority.MEDIUM,
        due_date=datetime.utcnow() + timedelta(days=7),
        recurrence_pattern_id=sample_recurrence_pattern.id,
        tags=["recurring"],
        completed=False
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@pytest.fixture(name="multiple_todos")
def multiple_todos_fixture(session: Session, sample_user_id: int) -> list[Todo]:
    """Create multiple todos with different properties for testing."""
    todos = [
        Todo(
            title=f"Todo {i}",
            description=f"Description {i}",
            user_id=sample_user_id,
            priority=TodoPriority.LOW if i % 3 == 0 else TodoPriority.MEDIUM,
            tags=["batch", f"tag{i}"],
            completed=i % 2 == 0,
            due_date=datetime.utcnow() + timedelta(days=i) if i % 2 == 1 else None
        )
        for i in range(10)
    ]
    
    for todo in todos:
        session.add(todo)
    
    session.commit()
    
    for todo in todos:
        session.refresh(todo)
    
    return todos


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture(name="freeze_time")
def freeze_time_fixture():
    """Fixture to freeze time for testing time-dependent functionality."""
    frozen_time = datetime(2026, 2, 11, 12, 0, 0)
    return frozen_time


@pytest.fixture(autouse=True)
def reset_database(session: Session):
    """Reset database between tests."""
    yield
    # Cleanup is handled by session fixture

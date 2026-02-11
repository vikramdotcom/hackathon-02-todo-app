"""
Database Seeding Script

Populates the database with sample data for development and testing.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from app.database import get_db_context, init_db
from app.models.todo import Todo, TodoPriority
from app.models.recurrence import RecurrencePattern, RecurrenceFrequency, RecurrenceEndCondition


def seed_recurrence_patterns():
    """Create sample recurrence patterns."""
    patterns = [
        RecurrencePattern(
            frequency=RecurrenceFrequency.DAILY,
            interval=1,
            end_condition=RecurrenceEndCondition.NEVER,
            next_occurrence=datetime.utcnow() + timedelta(days=1),
            occurrence_count=0
        ),
        RecurrencePattern(
            frequency=RecurrenceFrequency.WEEKLY,
            interval=1,
            end_condition=RecurrenceEndCondition.NEVER,
            next_occurrence=datetime.utcnow() + timedelta(days=7),
            occurrence_count=0,
            days_of_week=[0, 2, 4]  # Monday, Wednesday, Friday
        ),
        RecurrencePattern(
            frequency=RecurrenceFrequency.MONTHLY,
            interval=1,
            end_condition=RecurrenceEndCondition.AFTER_OCCURRENCES,
            end_after_occurrences=12,
            next_occurrence=datetime.utcnow() + timedelta(days=30),
            occurrence_count=0,
            day_of_month=1
        ),
    ]

    with get_db_context() as db:
        for pattern in patterns:
            db.add(pattern)
        db.commit()

        for pattern in patterns:
            db.refresh(pattern)

    print(f"✓ Created {len(patterns)} recurrence patterns")
    return patterns


def seed_todos(patterns):
    """Create sample todos."""
    todos = [
        # Regular todos
        Todo(
            title="Review pull requests",
            description="Review and merge pending PRs",
            user_id=1,
            priority=TodoPriority.HIGH,
            tags=["work", "code-review"],
            due_date=datetime.utcnow() + timedelta(days=1),
            completed=False
        ),
        Todo(
            title="Update documentation",
            description="Update API documentation with new endpoints",
            user_id=1,
            priority=TodoPriority.MEDIUM,
            tags=["documentation", "work"],
            due_date=datetime.utcnow() + timedelta(days=3),
            completed=False
        ),
        Todo(
            title="Buy groceries",
            description="Milk, eggs, bread, vegetables",
            user_id=1,
            priority=TodoPriority.LOW,
            tags=["personal", "shopping"],
            due_date=datetime.utcnow() + timedelta(days=2),
            completed=False
        ),
        # Recurring todos
        Todo(
            title="Daily standup meeting",
            description="Team sync at 9 AM",
            user_id=1,
            priority=TodoPriority.HIGH,
            tags=["work", "meetings"],
            due_date=datetime.utcnow() + timedelta(days=1),
            recurrence_pattern_id=patterns[0].id,
            reminder_offsets=[15, 60],
            completed=False
        ),
        Todo(
            title="Weekly team retrospective",
            description="Discuss what went well and what to improve",
            user_id=1,
            priority=TodoPriority.MEDIUM,
            tags=["work", "meetings", "team"],
            due_date=datetime.utcnow() + timedelta(days=7),
            recurrence_pattern_id=patterns[1].id,
            reminder_offsets=[1440],
            completed=False
        ),
        Todo(
            title="Monthly expense report",
            description="Submit expense report to finance",
            user_id=1,
            priority=TodoPriority.HIGH,
            tags=["work", "finance"],
            due_date=datetime.utcnow() + timedelta(days=30),
            recurrence_pattern_id=patterns[2].id,
            reminder_offsets=[2880, 1440],
            completed=False
        ),
        # Completed todos
        Todo(
            title="Setup development environment",
            description="Install dependencies and configure IDE",
            user_id=1,
            priority=TodoPriority.HIGH,
            tags=["work", "setup"],
            completed=True
        ),
        Todo(
            title="Read project documentation",
            description="Familiarize with codebase and architecture",
            user_id=1,
            priority=TodoPriority.MEDIUM,
            tags=["work", "learning"],
            completed=True
        ),
    ]

    with get_db_context() as db:
        for todo in todos:
            db.add(todo)
        db.commit()

    print(f"✓ Created {len(todos)} todos")
    print(f"  - {sum(1 for t in todos if not t.completed)} active")
    print(f"  - {sum(1 for t in todos if t.completed)} completed")
    print(f"  - {sum(1 for t in todos if t.recurrence_pattern_id)} recurring")


def main():
    """Main seeding function."""
    print("🌱 Seeding database with sample data...")
    print()

    # Initialize database
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")
    print()

    # Seed data
    patterns = seed_recurrence_patterns()
    seed_todos(patterns)

    print()
    print("✅ Database seeding complete!")
    print()
    print("You can now:")
    print("  - Start the backend: uvicorn app.main:app --reload")
    print("  - View API docs: http://localhost:8000/docs")
    print("  - Test endpoints with sample data")


if __name__ == "__main__":
    main()

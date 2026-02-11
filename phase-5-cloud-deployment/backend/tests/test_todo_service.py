"""
Unit Tests for TodoService

Tests todo service operations including:
- CRUD operations
- Filtering and search
- Recurring task completion
"""

import pytest
from datetime import datetime, timedelta
from app.services.todo_service import TodoService
from app.models.todo import TodoPriority


class TestTodoServiceCreate:
    """Test todo creation."""

    def test_create_basic_todo(self, session, sample_user_id):
        """Test creating a basic todo."""
        service = TodoService(session)
        todo = service.create_todo(
            title="Test Todo",
            user_id=sample_user_id,
            description="Test description"
        )
        
        assert todo.id is not None
        assert todo.title == "Test Todo"
        assert todo.description == "Test description"
        assert todo.user_id == sample_user_id
        assert todo.completed is False

    def test_create_todo_with_phase_v_fields(self, session, sample_user_id):
        """Test creating todo with Phase V fields."""
        service = TodoService(session)
        due_date = datetime.utcnow() + timedelta(days=7)
        
        todo = service.create_todo(
            title="Advanced Todo",
            user_id=sample_user_id,
            due_date=due_date,
            priority=TodoPriority.HIGH,
            tags=["work", "urgent"],
            reminder_offsets=[60, 1440]
        )
        
        assert todo.due_date == due_date
        assert todo.priority == TodoPriority.HIGH
        assert todo.tags == ["work", "urgent"]
        assert todo.reminder_offsets == [60, 1440]


class TestTodoServiceRead:
    """Test todo retrieval."""

    def test_get_todo_by_id(self, session, sample_user_id, sample_todo):
        """Test retrieving todo by ID."""
        service = TodoService(session)
        todo = service.get_todo(sample_todo.id, sample_user_id)
        
        assert todo is not None
        assert todo.id == sample_todo.id
        assert todo.title == sample_todo.title

    def test_get_todo_wrong_user(self, session, sample_todo):
        """Test that todo cannot be retrieved by wrong user."""
        service = TodoService(session)
        todo = service.get_todo(sample_todo.id, user_id=999)
        
        assert todo is None

    def test_list_todos_all(self, session, sample_user_id, multiple_todos):
        """Test listing all todos."""
        service = TodoService(session)
        todos = service.list_todos(user_id=sample_user_id)
        
        assert len(todos) == 10

    def test_list_todos_filter_by_completed(self, session, sample_user_id, multiple_todos):
        """Test filtering todos by completion status."""
        service = TodoService(session)
        completed_todos = service.list_todos(user_id=sample_user_id, completed=True)
        incomplete_todos = service.list_todos(user_id=sample_user_id, completed=False)
        
        assert len(completed_todos) == 5
        assert len(incomplete_todos) == 5

    def test_list_todos_filter_by_priority(self, session, sample_user_id, multiple_todos):
        """Test filtering todos by priority."""
        service = TodoService(session)
        low_priority = service.list_todos(user_id=sample_user_id, priority=TodoPriority.LOW)
        
        assert all(todo.priority == TodoPriority.LOW for todo in low_priority)


class TestTodoServiceUpdate:
    """Test todo updates."""

    def test_update_todo_title(self, session, sample_user_id, sample_todo):
        """Test updating todo title."""
        service = TodoService(session)
        updated = service.update_todo(
            sample_todo.id,
            sample_user_id,
            title="Updated Title"
        )
        
        assert updated is not None
        assert updated.title == "Updated Title"

    def test_update_todo_multiple_fields(self, session, sample_user_id, sample_todo):
        """Test updating multiple fields."""
        service = TodoService(session)
        updated = service.update_todo(
            sample_todo.id,
            sample_user_id,
            title="New Title",
            priority=TodoPriority.URGENT,
            tags=["updated"]
        )
        
        assert updated.title == "New Title"
        assert updated.priority == TodoPriority.URGENT
        assert updated.tags == ["updated"]


class TestTodoServiceDelete:
    """Test todo deletion."""

    def test_delete_todo(self, session, sample_user_id, sample_todo):
        """Test deleting a todo."""
        service = TodoService(session)
        deleted = service.delete_todo(sample_todo.id, sample_user_id)
        
        assert deleted is True
        
        # Verify it's gone
        todo = service.get_todo(sample_todo.id, sample_user_id)
        assert todo is None

    def test_delete_todo_wrong_user(self, session, sample_todo):
        """Test that todo cannot be deleted by wrong user."""
        service = TodoService(session)
        deleted = service.delete_todo(sample_todo.id, user_id=999)
        
        assert deleted is False


class TestTodoServiceComplete:
    """Test todo completion."""

    def test_complete_todo(self, session, sample_user_id, sample_todo):
        """Test completing a todo."""
        service = TodoService(session)
        completed = service.complete_todo(sample_todo.id, sample_user_id)
        
        assert completed is not None
        assert completed.completed is True

    def test_complete_recurring_todo_creates_next_instance(
        self, session, sample_user_id, sample_recurring_todo
    ):
        """Test that completing recurring todo creates next instance."""
        service = TodoService(session)
        
        # Complete the recurring todo
        completed = service.complete_todo(sample_recurring_todo.id, sample_user_id)
        assert completed.completed is True
        
        # Check that a new instance was created
        all_todos = service.list_todos(user_id=sample_user_id, completed=False)
        recurring_todos = [t for t in all_todos if t.is_recurring()]
        
        assert len(recurring_todos) >= 1


class TestTodoServiceSearch:
    """Test todo search functionality."""

    def test_search_todos_by_title(self, session, sample_user_id, multiple_todos):
        """Test searching todos by title."""
        service = TodoService(session)
        results = service.search_todos(user_id=sample_user_id, query="Todo 5")
        
        assert len(results) >= 1
        assert any("Todo 5" in todo.title for todo in results)

    def test_search_todos_case_insensitive(self, session, sample_user_id, multiple_todos):
        """Test that search is case insensitive."""
        service = TodoService(session)
        results = service.search_todos(user_id=sample_user_id, query="todo")
        
        assert len(results) > 0


class TestTodoServiceOverdue:
    """Test overdue todo functionality."""

    def test_get_overdue_todos(self, session, sample_user_id, sample_overdue_todo):
        """Test retrieving overdue todos."""
        service = TodoService(session)
        overdue = service.get_overdue_todos(sample_user_id)
        
        assert len(overdue) >= 1
        assert all(todo.is_overdue() for todo in overdue)


class TestTodoServiceUpcoming:
    """Test upcoming todo functionality."""

    def test_get_upcoming_todos(self, session, sample_user_id, sample_todo_with_due_date):
        """Test retrieving upcoming todos."""
        service = TodoService(session)
        upcoming = service.get_upcoming_todos(sample_user_id, days_ahead=30)
        
        assert len(upcoming) >= 1
        assert all(todo.due_date is not None for todo in upcoming)

"""
Extended Todo Service for Phase V

Integrates recurring task functionality with core todo operations.
Handles task completion with automatic next instance creation for recurring tasks.
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select, or_, and_
from app.models.todo import Todo, TodoPriority
from app.models.recurrence import RecurrencePattern
from app.services.recurrence_service import RecurrenceService
import logging

logger = logging.getLogger(__name__)


class TodoService:
    """
    Extended Todo service with Phase V recurring task support.

    Provides CRUD operations for todos with automatic handling of:
    - Recurring task instance creation
    - Due date management
    - Priority and tag filtering
    - Search functionality
    """

    def __init__(self, db_session: Session):
        """
        Initialize TodoService.

        Args:
            db_session: Database session for operations
        """
        self.db = db_session
        self.recurrence_service = RecurrenceService(db_session)

    def create_todo(
        self,
        title: str,
        user_id: int,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: TodoPriority = TodoPriority.MEDIUM,
        tags: Optional[List[str]] = None,
        recurrence_pattern_id: Optional[int] = None,
        reminder_offsets: Optional[List[int]] = None
    ) -> Todo:
        """
        Create a new todo with optional Phase V features.

        Args:
            title: Task title (required)
            user_id: Owner user ID
            description: Task description (optional)
            due_date: When the task is due (optional)
            priority: Task priority level
            tags: List of tags for categorization
            recurrence_pattern_id: Link to recurrence pattern if recurring
            reminder_offsets: Reminder offsets in minutes before due date

        Returns:
            Created Todo instance
        """
        todo = Todo(
            title=title,
            description=description,
            user_id=user_id,
            due_date=due_date,
            priority=priority,
            tags=tags,
            recurrence_pattern_id=recurrence_pattern_id,
            reminder_offsets=reminder_offsets,
            completed=False
        )

        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)

        logger.info(f"Created todo {todo.id}: {title} (user={user_id}, recurring={todo.is_recurring()})")
        return todo

    def get_todo(self, todo_id: int, user_id: int) -> Optional[Todo]:
        """
        Get a todo by ID, ensuring it belongs to the user.

        Args:
            todo_id: Todo ID to retrieve
            user_id: User ID for ownership verification

        Returns:
            Todo instance if found and owned by user, None otherwise
        """
        statement = select(Todo).where(
            and_(Todo.id == todo_id, Todo.user_id == user_id)
        )
        return self.db.exec(statement).first()

    def list_todos(
        self,
        user_id: int,
        completed: Optional[bool] = None,
        priority: Optional[TodoPriority] = None,
        tags: Optional[List[str]] = None,
        overdue_only: bool = False,
        recurring_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Todo]:
        """
        List todos with filtering options.

        Args:
            user_id: User ID to filter by
            completed: Filter by completion status (None = all)
            priority: Filter by priority level
            tags: Filter by tags (any match)
            overdue_only: Only return overdue tasks
            recurring_only: Only return recurring tasks
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of Todo instances matching filters
        """
        statement = select(Todo).where(Todo.user_id == user_id)

        # Apply filters
        if completed is not None:
            statement = statement.where(Todo.completed == completed)

        if priority is not None:
            statement = statement.where(Todo.priority == priority)

        if recurring_only:
            statement = statement.where(Todo.recurrence_pattern_id.isnot(None))

        if overdue_only:
            statement = statement.where(
                and_(
                    Todo.due_date.isnot(None),
                    Todo.due_date < datetime.utcnow(),
                    Todo.completed == False
                )
            )

        # Tag filtering (if tags are provided, match any)
        if tags:
            # PostgreSQL JSON contains operator
            tag_conditions = [Todo.tags.contains([tag]) for tag in tags]
            statement = statement.where(or_(*tag_conditions))

        # Order by due date (nulls last), then priority, then created_at
        statement = statement.order_by(
            Todo.due_date.asc().nullslast(),
            Todo.priority.desc(),
            Todo.created_at.desc()
        )

        # Apply pagination
        statement = statement.limit(limit).offset(offset)

        todos = self.db.exec(statement).all()
        logger.info(f"Listed {len(todos)} todos for user {user_id}")
        return todos

    def update_todo(
        self,
        todo_id: int,
        user_id: int,
        **updates
    ) -> Optional[Todo]:
        """
        Update a todo with new values.

        Args:
            todo_id: Todo ID to update
            user_id: User ID for ownership verification
            **updates: Fields to update

        Returns:
            Updated Todo instance if found and owned by user, None otherwise
        """
        todo = self.get_todo(todo_id, user_id)
        if not todo:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(todo, key) and key not in ['id', 'user_id', 'created_at']:
                setattr(todo, key, value)

        todo.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(todo)

        logger.info(f"Updated todo {todo_id}: {list(updates.keys())}")
        return todo

    def complete_todo(self, todo_id: int, user_id: int) -> Optional[Todo]:
        """
        Mark a todo as completed.

        If the todo is recurring, automatically creates the next instance.

        Args:
            todo_id: Todo ID to complete
            user_id: User ID for ownership verification

        Returns:
            Completed Todo instance, or None if not found
        """
        todo = self.get_todo(todo_id, user_id)
        if not todo:
            return None

        # Mark as completed
        todo.completed = True
        todo.updated_at = datetime.utcnow()

        # Handle recurring tasks
        if todo.is_recurring():
            pattern = self.db.get(RecurrencePattern, todo.recurrence_pattern_id)
            if pattern:
                next_instance = self.recurrence_service.create_next_instance(todo, pattern)
                if next_instance:
                    logger.info(
                        f"Created next instance {next_instance.id} for recurring todo {todo_id}"
                    )
                else:
                    logger.info(
                        f"Recurrence ended for todo {todo_id}, no next instance created"
                    )

        self.db.commit()
        self.db.refresh(todo)

        logger.info(f"Completed todo {todo_id}")
        return todo

    def delete_todo(self, todo_id: int, user_id: int) -> bool:
        """
        Delete a todo.

        Args:
            todo_id: Todo ID to delete
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False if not found or not owned by user
        """
        todo = self.get_todo(todo_id, user_id)
        if not todo:
            return False

        self.db.delete(todo)
        self.db.commit()

        logger.info(f"Deleted todo {todo_id}")
        return True

    def search_todos(
        self,
        user_id: int,
        query: str,
        limit: int = 50
    ) -> List[Todo]:
        """
        Search todos by title and description.

        Args:
            user_id: User ID to filter by
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching Todo instances
        """
        search_pattern = f"%{query}%"
        statement = select(Todo).where(
            and_(
                Todo.user_id == user_id,
                or_(
                    Todo.title.ilike(search_pattern),
                    Todo.description.ilike(search_pattern)
                )
            )
        ).limit(limit)

        todos = self.db.exec(statement).all()
        logger.info(f"Search '{query}' returned {len(todos)} results for user {user_id}")
        return todos

    def get_overdue_todos(self, user_id: int) -> List[Todo]:
        """
        Get all overdue todos for a user.

        Args:
            user_id: User ID to filter by

        Returns:
            List of overdue Todo instances
        """
        return self.list_todos(user_id, overdue_only=True, completed=False)

    def get_upcoming_todos(
        self,
        user_id: int,
        days_ahead: int = 7
    ) -> List[Todo]:
        """
        Get todos due within the next N days.

        Args:
            user_id: User ID to filter by
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming Todo instances
        """
        from datetime import timedelta

        end_date = datetime.utcnow() + timedelta(days=days_ahead)

        statement = select(Todo).where(
            and_(
                Todo.user_id == user_id,
                Todo.completed == False,
                Todo.due_date.isnot(None),
                Todo.due_date <= end_date,
                Todo.due_date >= datetime.utcnow()
            )
        ).order_by(Todo.due_date.asc())

        todos = self.db.exec(statement).all()
        logger.info(f"Found {len(todos)} upcoming todos for user {user_id}")
        return todos

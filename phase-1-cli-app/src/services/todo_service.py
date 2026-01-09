"""
TodoManager service for Phase I CLI Todo App.

This module provides the business logic layer for todo operations.
"""

from datetime import datetime
from typing import List, Optional
from src.models.todo import Todo
from src.models.session import Session


class TodoManager:
    """
    Service class for managing todo operations.

    Provides CRUD operations and filtering for todos within a session.
    """

    def __init__(self, session: Session):
        """
        Initialize TodoManager with a session.

        Args:
            session: Session object to manage
        """
        self.session = session

    def add_todo(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        recurrence: Optional[str] = None
    ) -> Todo:
        """
        Add a new todo to the session.

        Args:
            title: Todo title (required)
            description: Todo description (optional)
            priority: Priority level (low/medium/high)
            tags: List of tags (optional)
            due_date: Due date (optional)
            recurrence: Recurrence pattern (optional)

        Returns:
            Todo: The created todo object

        Raises:
            ValueError: If validation fails
        """
        # Generate unique ID
        todo_id = self.session.next_id
        self.session.next_id += 1

        # Create todo with current timestamp
        now = datetime.now()
        todo = Todo(
            id=todo_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags if tags else [],
            due_date=due_date,
            recurrence=recurrence,
            created_at=now,
            updated_at=now
        )

        # Add to session
        self.session.todos.append(todo)
        self.session.operations["added"] += 1

        return todo

    def get_all_todos(self) -> List[Todo]:
        """
        Get all todos in the session.

        Returns:
            List[Todo]: List of all todos
        """
        return self.session.todos

    def get_todo_by_id(self, todo_id: int) -> Todo:
        """
        Find and return a todo by ID.

        Args:
            todo_id: ID of the todo to find

        Returns:
            Todo: The found todo object

        Raises:
            ValueError: If todo with given ID is not found
        """
        for todo in self.session.todos:
            if todo.id == todo_id:
                return todo
        raise ValueError(f"Todo with ID {todo_id} not found")

    def update_todo(self, todo_id: int, **fields) -> Todo:
        """
        Update a todo's mutable fields.

        Args:
            todo_id: ID of the todo to update
            **fields: Fields to update (title, description, priority, tags, due_date, recurrence)

        Returns:
            Todo: The updated todo object

        Raises:
            ValueError: If todo not found or validation fails
        """
        todo = self.get_todo_by_id(todo_id)

        # Update mutable fields
        if "title" in fields:
            todo.title = fields["title"]
        if "description" in fields:
            todo.description = fields["description"]
        if "priority" in fields:
            todo.priority = fields["priority"]
        if "tags" in fields:
            todo.tags = fields["tags"]
        if "due_date" in fields:
            todo.due_date = fields["due_date"]
        if "recurrence" in fields:
            todo.recurrence = fields["recurrence"]

        # Update timestamp
        todo.updated_at = datetime.now()

        # Re-validate after updates
        todo._validate_title()
        todo._validate_priority()
        todo._validate_description()

        # Increment operations counter
        self.session.operations["updated"] += 1

        return todo

    def delete_todo(self, todo_id: int) -> None:
        """
        Delete a todo from the session.

        Args:
            todo_id: ID of the todo to delete

        Raises:
            ValueError: If todo with given ID is not found
        """
        todo = self.get_todo_by_id(todo_id)
        self.session.todos.remove(todo)
        self.session.operations["deleted"] += 1

    def mark_complete(self, todo_id: int) -> Todo:
        """
        Mark a todo as complete.

        Args:
            todo_id: ID of the todo to mark complete

        Returns:
            Todo: The updated todo object

        Raises:
            ValueError: If todo with given ID is not found
        """
        todo = self.get_todo_by_id(todo_id)
        todo.completed = True
        todo.updated_at = datetime.now()
        self.session.operations["completed"] += 1
        return todo

    def mark_incomplete(self, todo_id: int) -> Todo:
        """
        Mark a todo as incomplete.

        Args:
            todo_id: ID of the todo to mark incomplete

        Returns:
            Todo: The updated todo object

        Raises:
            ValueError: If todo with given ID is not found
        """
        todo = self.get_todo_by_id(todo_id)
        todo.completed = False
        todo.updated_at = datetime.now()
        return todo

    def filter_by_status(self, status: str) -> List[Todo]:
        """
        Filter todos by completion status.

        Args:
            status: "completed", "pending", or "all"

        Returns:
            List[Todo]: Filtered list of todos
        """
        if status == "all":
            return self.session.todos
        elif status == "completed":
            return [todo for todo in self.session.todos if todo.completed]
        elif status == "pending":
            return [todo for todo in self.session.todos if not todo.completed]
        else:
            return self.session.todos

    def filter_by_priority(self, priority: str) -> List[Todo]:
        """
        Filter todos by priority level.

        Args:
            priority: "high", "medium", "low", or "all"

        Returns:
            List[Todo]: Filtered list of todos
        """
        if priority == "all":
            return self.session.todos
        else:
            return [todo for todo in self.session.todos if todo.priority == priority]

    def filter_by_tag(self, tag: str) -> List[Todo]:
        """
        Filter todos by tag.

        Args:
            tag: Tag name to filter by

        Returns:
            List[Todo]: Filtered list of todos containing the tag
        """
        return [todo for todo in self.session.todos if tag in todo.tags]

    def get_session_summary(self) -> dict:
        """
        Get session statistics.

        Returns:
            dict: Session summary with counts
        """
        total_todos = len(self.session.todos)
        completed_count = sum(1 for todo in self.session.todos if todo.completed)
        pending_count = total_todos - completed_count

        return {
            "total_todos": total_todos,
            "completed_count": completed_count,
            "pending_count": pending_count,
            "operations": self.session.operations.copy()
        }

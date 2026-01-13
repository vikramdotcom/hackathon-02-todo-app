from sqlmodel import Session, select, col
from typing import Optional, List
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoService:
    """Service for todo-related operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_todo(self, user_id: int, todo_data: TodoCreate) -> Todo:
        """Create a new todo for a user."""
        todo = Todo(
            user_id=user_id,
            title=todo_data.title,
            description=todo_data.description or "",
            priority=todo_data.priority or "medium",
            tags=todo_data.tags or [],
            due_date=todo_data.due_date,
            recurrence=todo_data.recurrence
        )

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)

        return todo

    def get_todo_by_id(self, todo_id: int, user_id: int) -> Optional[Todo]:
        """Get a specific todo by ID (must belong to user)."""
        statement = select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_user_todos(
        self,
        user_id: int,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Todo], int]:
        """
        Get todos for a user with filtering, sorting, and pagination.

        Returns:
            Tuple of (todos list, total count)
        """
        # Base query
        statement = select(Todo).where(Todo.user_id == user_id)

        # Apply filters
        if completed is not None:
            statement = statement.where(Todo.completed == completed)

        if priority is not None:
            statement = statement.where(Todo.priority == priority)

        if tags is not None and len(tags) > 0:
            # Filter by any of the provided tags
            for tag in tags:
                statement = statement.where(col(Todo.tags).contains([tag]))

        if search is not None and search.strip():
            search_term = f"%{search}%"
            statement = statement.where(
                (Todo.title.ilike(search_term)) | (Todo.description.ilike(search_term))
            )

        # Get total count before pagination
        count_statement = statement
        total = len(self.session.exec(count_statement).all())

        # Apply sorting
        if sort_order == "asc":
            statement = statement.order_by(getattr(Todo, sort_by))
        else:
            statement = statement.order_by(getattr(Todo, sort_by).desc())

        # Apply pagination
        statement = statement.offset(skip).limit(limit)

        # Execute query
        todos = self.session.exec(statement).all()

        return list(todos), total

    def update_todo(self, todo_id: int, user_id: int, todo_data: TodoUpdate) -> Optional[Todo]:
        """Update a todo (must belong to user)."""
        todo = self.get_todo_by_id(todo_id, user_id)

        if not todo:
            return None

        # Update fields if provided
        if todo_data.title is not None:
            todo.title = todo_data.title

        if todo_data.description is not None:
            todo.description = todo_data.description

        if todo_data.completed is not None:
            todo.completed = todo_data.completed

        if todo_data.priority is not None:
            todo.priority = todo_data.priority

        if todo_data.tags is not None:
            todo.tags = todo_data.tags

        if todo_data.due_date is not None:
            todo.due_date = todo_data.due_date

        if todo_data.recurrence is not None:
            todo.recurrence = todo_data.recurrence

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)

        return todo

    def delete_todo(self, todo_id: int, user_id: int) -> bool:
        """Delete a todo (must belong to user)."""
        todo = self.get_todo_by_id(todo_id, user_id)

        if not todo:
            return False

        self.session.delete(todo)
        self.session.commit()

        return True

    def toggle_todo_completion(self, todo_id: int, user_id: int) -> Optional[Todo]:
        """Toggle the completion status of a todo."""
        todo = self.get_todo_by_id(todo_id, user_id)

        if not todo:
            return None

        todo.completed = not todo.completed

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)

        return todo

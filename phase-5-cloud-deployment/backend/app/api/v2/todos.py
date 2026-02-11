"""
API v2 Todos Router

Endpoints for managing todos with Phase V features:
- Recurring tasks
- Due dates and priorities
- Tags and reminders
- Search and filtering
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from app.api.v2.schemas import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoListResponse,
    TodoSearchRequest,
    ErrorResponse
)
from app.services.todo_service import TodoService
from app.models.todo import TodoPriority
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/todos", tags=["todos"])


# Import database dependency
from app.database import get_db


# Dependency to get current user ID (placeholder - implement based on your auth)
async def get_current_user_id() -> int:
    """
    Get current authenticated user ID.

    TODO: Implement proper authentication (JWT, OAuth, etc.)
    For now, returns a default user ID for development.
    """
    # In production, this would decode JWT token, verify session, etc.
    # For development/testing, return a default user ID
    return 1  # Default user ID for development


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
    responses={
        201: {"description": "Todo created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def create_todo(
    todo_data: TodoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TodoResponse:
    """
    Create a new todo with Phase V features.

    Supports:
    - Basic fields: title, description
    - Phase V fields: due_date, priority, tags, recurrence_pattern_id, reminder_offsets
    """
    try:
        service = TodoService(db)
        todo = service.create_todo(
            title=todo_data.title,
            user_id=user_id,
            description=todo_data.description,
            due_date=todo_data.due_date,
            priority=todo_data.priority,
            tags=todo_data.tags,
            recurrence_pattern_id=todo_data.recurrence_pattern_id,
            reminder_offsets=todo_data.reminder_offsets
        )
        return TodoResponse.from_todo(todo)
    except Exception as e:
        logger.error(f"Error creating todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=TodoListResponse,
    summary="List todos with filtering",
    responses={
        200: {"description": "Todos retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def list_todos(
    completed: Optional[bool] = Query(default=None, description="Filter by completion status"),
    priority: Optional[TodoPriority] = Query(default=None, description="Filter by priority"),
    tags: Optional[List[str]] = Query(default=None, description="Filter by tags (any match)"),
    overdue_only: bool = Query(default=False, description="Only return overdue tasks"),
    recurring_only: bool = Query(default=False, description="Only return recurring tasks"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TodoListResponse:
    """
    List todos with advanced filtering options.

    Filters:
    - completed: Filter by completion status
    - priority: Filter by priority level
    - tags: Filter by tags (matches any)
    - overdue_only: Only overdue tasks
    - recurring_only: Only recurring tasks
    """
    try:
        service = TodoService(db)
        todos = service.list_todos(
            user_id=user_id,
            completed=completed,
            priority=priority,
            tags=tags,
            overdue_only=overdue_only,
            recurring_only=recurring_only,
            limit=limit,
            offset=offset
        )

        todo_responses = [TodoResponse.from_todo(todo) for todo in todos]

        return TodoListResponse(
            todos=todo_responses,
            total=len(todo_responses),
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error listing todos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve todos"
        )


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Get a specific todo",
    responses={
        200: {"description": "Todo retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Todo not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TodoResponse:
    """Get a specific todo by ID."""
    service = TodoService(db)
    todo = service.get_todo(todo_id, user_id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found"
        )

    return TodoResponse.from_todo(todo)


@router.patch(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Update a todo",
    responses={
        200: {"description": "Todo updated successfully"},
        404: {"model": ErrorResponse, "description": "Todo not found"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TodoResponse:
    """
    Update a todo with new values.

    Only provided fields will be updated.
    """
    try:
        service = TodoService(db)

        # Build updates dict from non-None values
        updates = {
            k: v for k, v in todo_data.dict(exclude_unset=True).items()
            if v is not None
        }

        todo = service.update_todo(todo_id, user_id, **updates)

        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo {todo_id} not found"
            )

        return TodoResponse.from_todo(todo)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo {todo_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{todo_id}/complete",
    response_model=TodoResponse,
    summary="Mark todo as completed",
    responses={
        200: {"description": "Todo completed successfully"},
        404: {"model": ErrorResponse, "description": "Todo not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def complete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> TodoResponse:
    """
    Mark a todo as completed.

    If the todo is recurring, automatically creates the next instance.
    """
    service = TodoService(db)
    todo = service.complete_todo(todo_id, user_id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found"
        )

    return TodoResponse.from_todo(todo)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a todo",
    responses={
        204: {"description": "Todo deleted successfully"},
        404: {"model": ErrorResponse, "description": "Todo not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a todo permanently."""
    service = TodoService(db)
    deleted = service.delete_todo(todo_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found"
        )

    return None


@router.post(
    "/search",
    response_model=List[TodoResponse],
    summary="Search todos",
    responses={
        200: {"description": "Search results retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def search_todos(
    search_data: TodoSearchRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> List[TodoResponse]:
    """
    Search todos by title and description.

    Uses case-insensitive pattern matching.
    """
    service = TodoService(db)
    todos = service.search_todos(
        user_id=user_id,
        query=search_data.query,
        limit=search_data.limit
    )

    return [TodoResponse.from_todo(todo) for todo in todos]


@router.get(
    "/overdue/list",
    response_model=List[TodoResponse],
    summary="Get overdue todos",
    responses={
        200: {"description": "Overdue todos retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def get_overdue_todos(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> List[TodoResponse]:
    """Get all overdue todos for the current user."""
    service = TodoService(db)
    todos = service.get_overdue_todos(user_id)
    return [TodoResponse.from_todo(todo) for todo in todos]


@router.get(
    "/upcoming/list",
    response_model=List[TodoResponse],
    summary="Get upcoming todos",
    responses={
        200: {"description": "Upcoming todos retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def get_upcoming_todos(
    days_ahead: int = Query(default=7, ge=1, le=365, description="Days to look ahead"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> List[TodoResponse]:
    """Get todos due within the next N days."""
    service = TodoService(db)
    todos = service.get_upcoming_todos(user_id, days_ahead)
    return [TodoResponse.from_todo(todo) for todo in todos]

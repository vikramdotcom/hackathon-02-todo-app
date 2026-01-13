from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional, List
from app.core.database import get_session
from app.api.deps import get_current_user
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse
from app.schemas import MessageResponse
from app.services.todo_service import TodoService
from app.models.user import User

router = APIRouter()


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new todo for the authenticated user.

    - **title**: Todo title (required, 1-10000 characters)
    - **description**: Detailed description (optional)
    - **priority**: Priority level - low, medium, or high (default: medium)
    - **tags**: List of tags (optional)
    - **due_date**: Due date in ISO format (optional)
    - **recurrence**: Recurrence pattern (optional)
    """
    todo_service = TodoService(session)
    todo = todo_service.create_todo(current_user.id, todo_data)
    return todo


@router.get("", response_model=TodoListResponse)
async def get_todos(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high)$", description="Filter by priority"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (any match)"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|due_date|priority)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get todos for the authenticated user with filtering, sorting, and pagination.

    Filters:
    - **completed**: Filter by completion status (true/false)
    - **priority**: Filter by priority level (low/medium/high)
    - **tags**: Filter by tags (returns todos with any matching tag)
    - **search**: Search in title and description (case-insensitive)

    Sorting:
    - **sort_by**: Field to sort by (created_at, updated_at, due_date, priority)
    - **sort_order**: Sort order (asc/desc)

    Pagination:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    """
    todo_service = TodoService(session)
    todos, total = todo_service.get_user_todos(
        user_id=current_user.id,
        completed=completed,
        priority=priority,
        tags=tags,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )

    return TodoListResponse(
        todos=todos,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific todo by ID.

    The todo must belong to the authenticated user.
    """
    todo_service = TodoService(session)
    todo = todo_service.get_todo_by_id(todo_id, current_user.id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a todo.

    The todo must belong to the authenticated user.
    Only provided fields will be updated.
    """
    todo_service = TodoService(session)
    todo = todo_service.update_todo(todo_id, current_user.id, todo_data)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return todo


@router.delete("/{todo_id}", response_model=MessageResponse)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a todo.

    The todo must belong to the authenticated user.
    """
    todo_service = TodoService(session)
    success = todo_service.delete_todo(todo_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return MessageResponse(message="Todo deleted successfully")


@router.post("/{todo_id}/complete", response_model=TodoResponse)
async def mark_todo_complete(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Mark a todo as complete.

    The todo must belong to the authenticated user.
    """
    todo_service = TodoService(session)
    todo = todo_service.get_todo_by_id(todo_id, current_user.id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    todo.completed = True
    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo


@router.post("/{todo_id}/incomplete", response_model=TodoResponse)
async def mark_todo_incomplete(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Mark a todo as incomplete.

    The todo must belong to the authenticated user.
    """
    todo_service = TodoService(session)
    todo = todo_service.get_todo_by_id(todo_id, current_user.id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    todo.completed = False
    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.api.deps import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.models.user import User
from app.models.todo import Todo
from pydantic import BaseModel

router = APIRouter()


class UserStats(BaseModel):
    """User statistics response."""
    total_todos: int
    completed_todos: int
    pending_todos: int
    completion_rate: float
    priority_distribution: dict


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update current user's profile.

    - **username**: New username (optional, 3-50 characters)
    - **email**: New email address (optional)
    """
    user_service = UserService(session)
    updated_user = user_service.update_user(current_user.id, user_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


@router.get("/me/stats", response_model=UserStats)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get statistics for current user's todos.

    Returns:
    - Total number of todos
    - Number of completed todos
    - Number of pending todos
    - Completion rate (percentage)
    - Priority distribution (count by priority level)
    """
    # Get total todos
    total_statement = select(func.count(Todo.id)).where(Todo.user_id == current_user.id)
    total_todos = session.exec(total_statement).one()

    # Get completed todos
    completed_statement = select(func.count(Todo.id)).where(
        Todo.user_id == current_user.id,
        Todo.completed == True
    )
    completed_todos = session.exec(completed_statement).one()

    # Calculate pending todos
    pending_todos = total_todos - completed_todos

    # Calculate completion rate
    completion_rate = (completed_todos / total_todos * 100) if total_todos > 0 else 0.0

    # Get priority distribution
    low_statement = select(func.count(Todo.id)).where(
        Todo.user_id == current_user.id,
        Todo.priority == "low"
    )
    low_count = session.exec(low_statement).one()

    medium_statement = select(func.count(Todo.id)).where(
        Todo.user_id == current_user.id,
        Todo.priority == "medium"
    )
    medium_count = session.exec(medium_statement).one()

    high_statement = select(func.count(Todo.id)).where(
        Todo.user_id == current_user.id,
        Todo.priority == "high"
    )
    high_count = session.exec(high_statement).one()

    return UserStats(
        total_todos=total_todos,
        completed_todos=completed_todos,
        pending_todos=pending_todos,
        completion_rate=round(completion_rate, 2),
        priority_distribution={
            "low": low_count,
            "medium": medium_count,
            "high": high_count
        }
    )

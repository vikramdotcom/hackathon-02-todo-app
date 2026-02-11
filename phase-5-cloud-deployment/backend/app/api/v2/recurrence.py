"""
API v2 Recurrence Patterns Router

Endpoints for managing recurrence patterns:
- Create, read, update, delete patterns
- View active patterns
- Calculate next occurrences
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from app.api.v2.schemas import (
    RecurrencePatternCreate,
    RecurrencePatternUpdate,
    RecurrencePatternResponse,
    RecurringTodoCreate,
    RecurringTodoResponse,
    ErrorResponse
)
from app.services.recurrence_service import RecurrenceService
from app.services.todo_service import TodoService
from app.models.recurrence import RecurrencePattern
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recurrence-patterns", tags=["recurrence"])


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
    response_model=RecurrencePatternResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a recurrence pattern",
    responses={
        201: {"description": "Recurrence pattern created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def create_recurrence_pattern(
    pattern_data: RecurrencePatternCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> RecurrencePatternResponse:
    """
    Create a new recurrence pattern.

    Supports:
    - Daily, weekly, monthly, yearly, and custom frequencies
    - End conditions: never, after N occurrences, or by date
    - Advanced scheduling: specific days of week, day of month, month of year
    """
    try:
        service = RecurrenceService(db)
        pattern = service.create_recurrence_pattern(
            frequency=pattern_data.frequency,
            interval=pattern_data.interval,
            end_condition=pattern_data.end_condition,
            end_after_occurrences=pattern_data.end_after_occurrences,
            end_by_date=pattern_data.end_by_date,
            days_of_week=pattern_data.days_of_week,
            day_of_month=pattern_data.day_of_month,
            month_of_year=pattern_data.month_of_year,
            start_date=pattern_data.start_date
        )
        return RecurrencePatternResponse.from_orm(pattern)
    except Exception as e:
        logger.error(f"Error creating recurrence pattern: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{pattern_id}",
    response_model=RecurrencePatternResponse,
    summary="Get a recurrence pattern",
    responses={
        200: {"description": "Recurrence pattern retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Pattern not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def get_recurrence_pattern(
    pattern_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> RecurrencePatternResponse:
    """Get a specific recurrence pattern by ID."""
    pattern = db.get(RecurrencePattern, pattern_id)

    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurrence pattern {pattern_id} not found"
        )

    return RecurrencePatternResponse.from_orm(pattern)


@router.patch(
    "/{pattern_id}",
    response_model=RecurrencePatternResponse,
    summary="Update a recurrence pattern",
    responses={
        200: {"description": "Pattern updated successfully"},
        404: {"model": ErrorResponse, "description": "Pattern not found"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def update_recurrence_pattern(
    pattern_id: int,
    pattern_data: RecurrencePatternUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> RecurrencePatternResponse:
    """
    Update a recurrence pattern.

    Only provided fields will be updated.
    Note: Updating a pattern affects all future instances, not past ones.
    """
    try:
        service = RecurrenceService(db)

        # Build updates dict from non-None values
        updates = {
            k: v for k, v in pattern_data.dict(exclude_unset=True).items()
            if v is not None
        }

        pattern = service.update_recurrence_pattern(pattern_id, **updates)
        return RecurrencePatternResponse.from_orm(pattern)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating recurrence pattern {pattern_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{pattern_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recurrence pattern",
    responses={
        204: {"description": "Pattern deleted successfully"},
        404: {"model": ErrorResponse, "description": "Pattern not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def delete_recurrence_pattern(
    pattern_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete a recurrence pattern.

    Warning: This will set recurrence_pattern_id to NULL for all associated todos.
    Existing todo instances will remain, but no new instances will be created.
    """
    service = RecurrenceService(db)
    deleted = service.delete_recurrence_pattern(pattern_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurrence pattern {pattern_id} not found"
        )

    return None


@router.get(
    "/active/list",
    response_model=List[RecurrencePatternResponse],
    summary="Get active recurrence patterns",
    responses={
        200: {"description": "Active patterns retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def get_active_patterns(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> List[RecurrencePatternResponse]:
    """
    Get all active recurrence patterns that haven't ended.

    Returns patterns where:
    - next_occurrence is in the past or now
    - End condition hasn't been met
    """
    service = RecurrenceService(db)
    patterns = service.get_active_patterns()
    return [RecurrencePatternResponse.from_orm(p) for p in patterns]


@router.post(
    "/recurring-todo",
    response_model=RecurringTodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a recurring todo with inline pattern",
    responses={
        201: {"description": "Recurring todo created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def create_recurring_todo(
    data: RecurringTodoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> RecurringTodoResponse:
    """
    Create a recurring todo with an inline recurrence pattern.

    This is a convenience endpoint that creates both the pattern and the todo
    in a single request, ensuring they're properly linked.
    """
    try:
        # Create recurrence pattern
        recurrence_service = RecurrenceService(db)
        pattern = recurrence_service.create_recurrence_pattern(
            frequency=data.recurrence_pattern.frequency,
            interval=data.recurrence_pattern.interval,
            end_condition=data.recurrence_pattern.end_condition,
            end_after_occurrences=data.recurrence_pattern.end_after_occurrences,
            end_by_date=data.recurrence_pattern.end_by_date,
            days_of_week=data.recurrence_pattern.days_of_week,
            day_of_month=data.recurrence_pattern.day_of_month,
            month_of_year=data.recurrence_pattern.month_of_year,
            start_date=data.recurrence_pattern.start_date
        )

        # Create todo with pattern
        todo_service = TodoService(db)
        todo = todo_service.create_todo(
            title=data.todo.title,
            user_id=user_id,
            description=data.todo.description,
            due_date=data.todo.due_date,
            priority=data.todo.priority,
            tags=data.todo.tags,
            recurrence_pattern_id=pattern.id,
            reminder_offsets=data.todo.reminder_offsets
        )

        from app.api.v2.schemas import TodoResponse

        return RecurringTodoResponse(
            todo=TodoResponse.from_todo(todo),
            recurrence_pattern=RecurrencePatternResponse.from_orm(pattern)
        )
    except Exception as e:
        logger.error(f"Error creating recurring todo: {e}")
        # Rollback will happen automatically if we raise an exception
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

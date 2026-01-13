from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TodoCreate(BaseModel):
    """Schema for creating a new todo."""
    title: str = Field(min_length=1, max_length=10000)
    description: Optional[str] = Field(default="", max_length=10000)
    priority: Optional[str] = Field(default="medium", pattern="^(low|medium|high)$")
    tags: Optional[List[str]] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = Field(default=None, max_length=100)


class TodoUpdate(BaseModel):
    """Schema for updating an existing todo."""
    title: Optional[str] = Field(None, min_length=1, max_length=10000)
    description: Optional[str] = Field(None, max_length=10000)
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = Field(None, max_length=100)


class TodoResponse(BaseModel):
    """Schema for todo response."""
    id: int
    user_id: int
    title: str
    description: str
    completed: bool
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    recurrence: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodoListResponse(BaseModel):
    """Schema for paginated todo list response."""
    todos: List[TodoResponse]
    total: int
    skip: int
    limit: int

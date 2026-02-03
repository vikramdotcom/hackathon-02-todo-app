from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List


class Todo(SQLModel, table=True):
    """Todo model with Phase I canonical schema plus user ownership."""

    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=10000, nullable=False)
    description: str = Field(default="", nullable=False)
    completed: bool = Field(default=False, nullable=False)
    priority: str = Field(default="medium", max_length=10, nullable=False)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for Phase II",
                "priority": "high",
                "tags": ["work", "documentation"],
                "due_date": "2026-01-15T17:00:00Z"
            }
        }

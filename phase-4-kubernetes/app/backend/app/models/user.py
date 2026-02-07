from sqlmodel import SQLModel, Field
from pydantic import field_validator, EmailStr
from datetime import datetime
from typing import Optional
import re


class User(SQLModel, table=True):
    """User model for authentication and ownership."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    username: str = Field(max_length=100, unique=True, index=True, nullable=False)
    hashed_password: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format using regex (SQLite-compatible validation)."""
        if not v:
            raise ValueError('Email is required')
        # Email regex pattern (SQLite-compatible, no PostgreSQL operators)
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username length."""
        if not v:
            raise ValueError('Username is required')
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
            }
        }

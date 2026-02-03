from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_session
from app.core.security import decode_access_token
from app.core.config import settings
from app.services.user_service import UserService
from app.models.user import User

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


def _create_test_user() -> User:
    """
    Creates a test user for authentication bypass mode.
    This user is used when DISABLE_AUTH is True.
    """
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        hashed_password="not_used_in_test_mode",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    When DISABLE_AUTH is True (set in .env), authentication is bypassed
    and a test user is returned. This is useful for testing the API
    without needing to authenticate.

    Raises:
        HTTPException: If token is invalid or user not found (when auth is enabled)
    """
    # ========== AUTHENTICATION BYPASS MODE ==========
    # When DISABLE_AUTH=True in .env, skip authentication and return test user
    if settings.DISABLE_AUTH:
        return _create_test_user()
    # ================================================

    # Normal authentication flow
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert string to int (JWT spec requires sub to be a string)
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService(session)
    user = user_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

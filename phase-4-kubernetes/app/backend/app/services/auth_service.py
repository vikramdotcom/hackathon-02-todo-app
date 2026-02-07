from datetime import timedelta
from typing import Optional
from sqlmodel import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.user_service import UserService
from app.core.security import verify_password, create_access_token
from app.core.config import settings


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: Session):
        self.session = session
        self.user_service = UserService(session)

    def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.

        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        existing_user = self.user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if username already exists
        existing_user = self.user_service.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create new user
        user = self.user_service.create_user(user_data)
        return user

    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate user with email and password.

        Returns:
            User if authentication successful, None otherwise
        """
        user = self.user_service.get_user_by_email(login_data.email)

        if not user:
            return None

        if not verify_password(login_data.password, user.hashed_password):
            return None

        return user

    def create_access_token_for_user(self, user: User) -> Token:
        """Create JWT access token for authenticated user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")

    def login(self, login_data: UserLogin) -> Token:
        """
        Login user and return access token.

        Raises:
            HTTPException: If authentication fails
        """
        user = self.authenticate_user(login_data)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self.create_access_token_for_user(user)

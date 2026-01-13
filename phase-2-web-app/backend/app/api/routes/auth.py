from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_user
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas import MessageResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user account.

    - **email**: Valid email address (unique)
    - **username**: Username between 3-50 characters (unique)
    - **password**: Password with minimum 8 characters
    """
    auth_service = AuthService(session)
    user = auth_service.register_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Login with email and password to receive JWT access token.

    - **email**: Registered email address
    - **password**: User password
    """
    auth_service = AuthService(session)
    token = auth_service.login(login_data)
    return token


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user (client-side token removal).

    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token from storage.
    """
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return current_user

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
import uuid
import jwt

from src.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from src.schemas.user import UserRead
from src.models.user import User
from src.services.auth_service import AuthService
from src.api.deps import get_db_session
from src.config.settings import settings
from src.utils.jwt import validate_and_decode_token

router = APIRouter()

security = HTTPBearer()


@router.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: RegisterRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user with email and password.
    This endpoint creates a new user in the database.
    """
    try:
        user = AuthService.register_user(user_data.email, user_data.password)
        return RegisterResponse(
            user_id=user.id,
            email=user.email
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/auth/login", response_model=LoginResponse)
async def login_user(
    login_data: LoginRequest
):
    """
    Authenticate user and return JWT token.
    NOTE: This is a simplified implementation for testing purposes.
    In production, Better Auth on the frontend should handle authentication.
    """
    try:
        user = AuthService.authenticate_user(login_data.email, login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Create a JWT token similar to what Better Auth would create
        # This is for testing purposes only - normally tokens come from Better Auth
        token_data = {
            "sub": str(user.id),  # User ID as subject
            "email": user.email,
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())  # 1 hour expiry
        }

        access_token = jwt.encode(
            token_data,
            settings.BETTER_AUTH_SECRET,
            algorithm="HS256"
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/auth/logout")
async def logout_user():
    """
    Logout user.
    In a real implementation, this might involve token blacklisting.
    """
    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserRead)
async def get_current_user(
    token: str = Depends(security)
):
    """
    Get current authenticated user's profile.
    """
    try:
        # Validate the token using the same function the other endpoints use
        token_data = validate_and_decode_token(token.credentials)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Find the user in the database using the email from the token
        user = AuthService.get_current_user(token.credentials)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserRead(id=user.id, email=user.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

from datetime import datetime